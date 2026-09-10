"""Shared analytics for the Phase 3 review ritual (read-only).

Nothing here may alter strategy state. It reads Supabase, reuses the
engine's own arithmetic (net_return, momentum) so the review can never
disagree with the engine, and computes the honest context a bare number
lacks: expectancy percentile bands, streak probabilities, and the frozen
GO_LIVE_BENCHMARK gate status.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from candle_lib import get_supabase  # noqa: E402
from backtest.loader import fetch_recent_4h  # noqa: E402
from signal_engine import PRIMARY, OBSERVATIONAL, STRATEGY_ID, net_return  # noqa: E402
from config.paper_account import INITIAL_CAPITAL_USD, KILL_SWITCH_DD  # noqa: E402

# Phase 1d ETH validation profile - the yardstick every comparison uses.
EXP = {
    "ETHUSDT": {"expectancy": 1.63, "win_rate": 0.26, "avg_win": 0.116, "avg_loss": -0.019},
    "BTCUSDT": {"expectancy": -0.09, "win_rate": 0.289, "avg_win": 0.035, "avg_loss": -0.0155},
}
EXPECTED_TRADES_PER_MONTH = 5.8  # combined, per PHASE1D_VERDICT
MIN_TRADES = 30


def myt(iso, fmt="%Y-%m-%d %H:%M"):
    if not iso:
        return "-"
    t = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return (t + timedelta(hours=8)).strftime(fmt)


def _dt(iso):
    t = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)


def load_all(client):
    trades = client.table("trades").select("*").order("id").execute().data
    signals = client.table("signals").select("*").order("id").execute().data
    state = {r["key"]: r for r in client.table("engine_state").select("*").execute().data}
    return trades, signals, state


def group_stats(trades, symbol):
    """Stats for ONE group. ETH manual and BTC observational never mix."""
    g = [t for t in trades if t["symbol"] == symbol]
    closed = [t for t in g if t["outcome"] != "open"]
    openp = [t for t in g if t["outcome"] == "open"]
    pcts = [float(t["pnl_pct"]) * 100 for t in closed]
    wins = [p for p in pcts if p > 0]
    losses = [p for p in pcts if p <= 0]
    return {
        "symbol": symbol,
        "closed": closed,
        "open": openp,
        "n": len(closed),
        "pcts": pcts,
        "win_rate": (len(wins) / len(pcts) * 100) if pcts else float("nan"),
        "avg_win": (sum(wins) / len(wins)) if wins else float("nan"),
        "avg_loss": (sum(losses) / len(losses)) if losses else float("nan"),
        "expectancy": (sum(pcts) / len(pcts)) if pcts else float("nan"),
        "realized_usd": sum(float(t["pnl_usd"] or 0) for t in closed),
        "weak": len(pcts) < MIN_TRADES,
    }


def percentile_bands(symbol, n, sims=60_000, seed=7):
    """Where a realized expectancy SHOULD sit after n trades if the strategy
    performs exactly as backtested. A number without its band invites panic."""
    if n < 1:
        return None
    e = EXP[symbol]
    rng = np.random.default_rng(seed)
    wins = rng.random((sims, n)) < e["win_rate"]
    res = np.where(wins, e["avg_win"], e["avg_loss"]).mean(axis=1) * 100
    return {q: float(np.percentile(res, q)) for q in (5, 25, 50, 75, 95)}


def streak_context(pcts, symbol, sims=40_000, seed=11):
    """Current and longest losing streak, plus how ordinary that is."""
    cur = 0
    for p in reversed(pcts):
        if p <= 0:
            cur += 1
        else:
            break
    longest = best = 0
    for p in pcts:
        best = best + 1 if p <= 0 else 0
        longest = max(longest, best)

    prob = float("nan")
    n = len(pcts)
    if n >= 2 and longest > 0:
        e = EXP[symbol]
        rng = np.random.default_rng(seed)
        w = rng.random((sims, n)) < e["win_rate"]
        run = np.zeros(sims, dtype=int)
        bestv = np.zeros(sims, dtype=int)
        for i in range(n):
            run = np.where(w[:, i], 0, run + 1)
            bestv = np.maximum(bestv, run)
        prob = float((bestv >= longest).mean() * 100)
    return {"current": cur, "longest": longest, "prob_at_least_this_long": prob}


def drop_best_test(pcts):
    """Benchmark criterion 4: remove the single largest winner - still >= 0?"""
    if len(pcts) < 2:
        return None
    trimmed = sorted(pcts)[:-1]
    return sum(trimmed) / len(trimmed)


def eth_slippage(trades, signals):
    """The measured gap between model and human: signal reference price vs
    the owner's actual logged fill. Phase 3's most valuable output."""
    by_id = {s["id"]: s for s in signals}
    rows = []
    for t in trades:
        if t["symbol"] != PRIMARY or not t.get("signal_id"):
            continue
        sig = by_id.get(t["signal_id"])
        if not sig or sig.get("entry_price") is None:
            continue
        ref = float(sig["entry_price"])
        actual = float(t["entry_actual"]) if t.get("entry_actual") else None
        if actual is None:
            continue
        # entry: paying above reference is adverse. exit: selling below is adverse.
        slip = (actual - ref) / ref * 100
        adverse = slip if sig["signal_type"] == "entry" else -slip
        lateness_h = None
        if sig.get("bar_open_time") and t.get("opened_at"):
            bar_close = _dt(sig["bar_open_time"]) + timedelta(hours=4)
            lateness_h = (_dt(t["opened_at"]) - bar_close).total_seconds() / 3600
        rows.append({
            "trade_id": t["id"], "signal_id": sig["id"], "type": sig["signal_type"],
            "ref": ref, "actual": actual, "slip_pct": slip,
            "adverse_pct": adverse, "lateness_h": lateness_h,
        })
    return rows


def unlogged_eth_signals(signals):
    """An unlogged ETH signal is a process failure - it silently corrupts
    the sample (August: a 2-day delay dropped two entry signals entirely)."""
    return [s for s in signals if s["symbol"] == PRIMARY and s["status"] == "pending"]


def equity_now(client, trades):
    eth_closed = sum(float(t["pnl_usd"] or 0) for t in trades
                     if t["symbol"] == PRIMARY and t["outcome"] != "open")
    mtm = 0.0
    price = None
    openp = [t for t in trades if t["symbol"] == PRIMARY and t["outcome"] == "open"]
    if openp:
        price = float(fetch_recent_4h(PRIMARY)["Close"].iloc[-1])
        t = openp[0]
        mtm = float(t["size_usd"]) * net_return(float(t["entry_actual"]), price)
    return INITIAL_CAPITAL_USD + eth_closed + mtm, eth_closed, mtm, price


def hodl_compare(trades, price):
    """Return AND max drawdown, both sides, over the live window."""
    eths = [t for t in trades if t["symbol"] == PRIMARY]
    if not eths or price is None:
        return None
    start_dt = min(_dt(t["opened_at"]) for t in eths)
    first_entry = float(sorted(eths, key=lambda x: x["opened_at"])[0]["entry_actual"])
    df = fetch_recent_4h(PRIMARY)
    win = df["Close"].to_numpy()[df.index >= start_dt.replace(tzinfo=None)]
    hodl_dd = float((win / np.maximum.accumulate(win) - 1).min() * 100) if len(win) else 0.0
    return {
        "start": start_dt, "days": (datetime.now(timezone.utc) - start_dt).days,
        "hodl_return": (price / first_entry - 1) * 100,
        "hodl_max_dd": hodl_dd,
        "eth_price_dd": hodl_dd,
    }
