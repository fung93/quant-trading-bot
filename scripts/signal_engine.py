"""Signal engine - Phase 2, paper mode. Runs every 4h via GitHub Actions.

Strategy: tsmom_v1, imported from strategies/tsmom_v1.py (parameters) and
backtest/indicators.py (momentum/ATR math) - the engine reimplements no
strategy arithmetic, so it cannot drift from what the lab validated. The
one rule mirrored here (and kept in sync by eye, it is two comparisons) is
the entry/exit condition from TsmomV1.next(): enter on momentum crossing
<=0 -> >0, exit on momentum <=0 or stop hit.

Symbols: ETHUSDT primary (owner logs fills manually via the dashboard),
BTCUSDT observational (engine auto-fills hypothetical trades at the next
bar's open; clearly labeled; excluded from equity and the kill switch).

Paper equity = INITIAL_CAPITAL + closed ETH PnL + open ETH mark-to-market.
Kill switch: 10% peak-to-trough halts NEW entries (exits still managed),
fires a Telegram alert, manual reset only (see README).

Evaluates ONLY the last CLOSED 4h candle (the resampler drops the forming
bin; the workflow runs sync first so candles are fresh). Idempotent: one
signal per (strategy, symbol, bar_open_time, signal_type) via unique-index
upsert - re-runs cannot duplicate. Telegram failure never loses a signal:
rows persist with telegram_sent=false and are retried next run.

Exit non-zero on failure so the Actions run goes red.
"""

import math
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from candle_lib import get_supabase  # scripts/ sibling

# The strategy file imports `backtesting` (the lab framework), which is
# deliberately NOT installed on the signal cron - it would drag bokeh etc.
# into a 6x/day job. The engine only reads the class's parameter attributes,
# so when the package is absent we register a minimal stand-in whose
# Strategy is a plain object. Parameters still come from the immutable
# strategy file - no values are re-typed here.
try:
    import backtesting  # noqa: F401
except ModuleNotFoundError:
    import types

    _stub = types.ModuleType("backtesting")
    _stub.Strategy = object
    sys.modules["backtesting"] = _stub

from backtest.indicators import atr, momentum
from backtest.loader import fetch_recent_4h
from config.paper_account import (
    COST_PER_SIDE,
    INITIAL_CAPITAL_USD,
    KILL_SWITCH_DD,
    MAX_POSITION_PCT,
    MYR_PER_USD,
    RISK_PER_TRADE,
)
from strategies.tsmom_v1 import BARS_PER_DAY, TsmomV1

STRATEGY_ID = "tsmom_v1"
PRIMARY = "ETHUSDT"
OBSERVATIONAL = "BTCUSDT"
LOOKBACK_N = TsmomV1.lookback_days * BARS_PER_DAY
ATR_MULT = TsmomV1.atr_mult
ATR_N = TsmomV1.atr_n
HISTORY_DAYS = 210  # 180-bar momentum + ATR + buffer

# Frozen evidence summary from PHASE1D_VERDICT.md - context for reasoning.
BACKTEST_STATS = {
    "ETHUSDT": {
        "window": "validation 2024-01 .. 2026-06",
        "trades": 80, "expectancy_pct_after_fees": 1.63, "win_rate_pct": 26.3,
        "avg_win_pct": 11.59, "avg_loss_pct": -1.92, "max_dd_pct": -16.6,
        "classification": "validated cell (first in lab)",
    },
    "BTCUSDT": {
        "window": "validation 2024-01 .. 2026-06",
        "trades": 90, "expectancy_pct_after_fees": -0.09, "win_rate_pct": 28.9,
        "avg_win_pct": 3.50, "avg_loss_pct": -1.55, "max_dd_pct": -23.1,
        "classification": "flat after fees - observational only",
    },
}


# ---------------------------------------------------------------- utilities

def myt(ts) -> str:
    """UTC timestamp -> 'YYYY-MM-DD HH:MM MYT' (UTC+8) for messages."""
    t = ts if isinstance(ts, datetime) else ts.to_pydatetime()
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return (t + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M MYT")


def tg_send(text: str) -> bool:
    """Send a Telegram message. Never raises; returns success. A failure
    must not crash signal writing - rows persist and are retried."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print("telegram: not configured, skipping send", flush=True)
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat, "text": text},
            timeout=15,
        )
        if r.status_code == 200:
            return True
        print(f"telegram: HTTP {r.status_code} {r.text[:200]}", file=sys.stderr)
    except requests.RequestException as exc:
        print(f"telegram: send failed: {exc}", file=sys.stderr)
    return False


def get_state(client, key: str, default):
    res = client.table("engine_state").select("value").eq("key", key).execute()
    return res.data[0]["value"] if res.data else default


def set_state(client, key: str, value: dict) -> None:
    client.table("engine_state").upsert(
        {"key": key, "value": value, "updated_at": datetime.now(timezone.utc).isoformat()},
        on_conflict="key",
    ).execute()


def net_return(entry_price: float, exit_price: float) -> float:
    """Round-trip return after the measured fee model (both sides)."""
    return (exit_price / entry_price) * (1 - COST_PER_SIDE) / (1 + COST_PER_SIDE) - 1


def entry_cross(mom) -> bool:
    """TsmomV1's entry condition: momentum crossed <=0 -> >0 at the last bar."""
    return len(mom) >= 2 and mom[-2] <= 0 < mom[-1]


def size_position(equity: float, price: float, atr_value: float) -> dict | None:
    """Risk-based sizing: a stop-out loses RISK_PER_TRADE of equity; position
    value capped at MAX_POSITION_PCT of equity (spot, no leverage)."""
    if math.isnan(atr_value) or atr_value <= 0:
        return None
    stop = price - ATR_MULT * atr_value
    if stop <= 0:
        return None
    risk_usd = equity * RISK_PER_TRADE
    units = risk_usd / (price - stop)
    size_usd = units * price
    cap = MAX_POSITION_PCT * equity
    if size_usd > cap:
        size_usd = cap
        units = size_usd / price
    return {"stop": stop, "risk_usd": risk_usd, "units": units, "size_usd": size_usd}


def find_live_cross(mom, start_idx: int) -> int | None:
    """Catch-up cross detection (GitHub skips/delays scheduled runs, so the
    newest bar is not always the bar a cross happened on).

    Walk back from the newest bar over the un-evaluated range [start_idx..n):
    if momentum at any bar on the way is <= 0 (or NaN), the most recent cross
    already died inside the gap - the strategy would be flat now, so no entry
    (the moment truly passed; we do not trade the past). If bar i is the
    transition mom[i-1] <= 0 < mom[i] and every bar from i to the newest
    stayed positive, that cross is still LIVE: the strategy would be long
    right now, so a (possibly late) entry signal is faithful to it.
    """
    n = len(mom)
    for i in range(n - 1, max(start_idx, 1) - 1, -1):
        if not mom[i] > 0:  # NaN-safe: NaN or <= 0 kills the cross
            return None
        if mom[i - 1] <= 0:
            return i
    return None


def get_last_evaluated(client, symbol: str):
    """Newest bar a previous run evaluated for this symbol, or None."""
    import pandas as pd

    v = get_state(client, f"last_evaluated_bar_{symbol}", {"bar": None})
    return pd.Timestamp(v["bar"]).tz_localize(None) if v.get("bar") else None


def last_exit_bar(client, symbol: str):
    """Bar of the most recent COMPLETED exit for this symbol, or None.

    While a position is open the engine evaluates exits only - it never looks
    for entry crosses. So if an exit signal sits unlogged for a while (ETH is
    filled by hand), any entry cross in that window was never scanned, and the
    plain last-evaluated marker has already drifted past it. Entry scanning
    must therefore resume from the EXIT bar, not from the marker. Observed
    2026-08-16: two ETH crosses missed across a 2-day logging delay.
    """
    import pandas as pd

    res = (
        client.table("signals")
        .select("bar_open_time")
        .eq("strategy", STRATEGY_ID)
        .eq("symbol", symbol)
        .eq("signal_type", "exit")
        .eq("status", "filled")
        .order("bar_open_time", desc=True)
        .limit(1)
        .execute()
    )
    if not res.data:
        return None
    return pd.Timestamp(res.data[0]["bar_open_time"]).tz_localize(None)


def set_last_evaluated(client, symbol: str, bar) -> None:
    set_state(client, f"last_evaluated_bar_{symbol}", {"bar": bar.isoformat()})


# ------------------------------------------------------------- DB accessors

def open_trade(client, symbol: str):
    res = (
        client.table("trades").select("*")
        .eq("symbol", symbol).eq("strategy", STRATEGY_ID)
        .eq("mode", "paper").eq("outcome", "open")
        .order("opened_at", desc=True).limit(1).execute()
    )
    return res.data[0] if res.data else None


def eth_equity(client, eth_last_close: float | None) -> float:
    """Paper equity: initial + closed ETH PnL + open ETH mark-to-market.
    BTC observational trades deliberately excluded."""
    closed = (
        client.table("trades").select("pnl_usd")
        .eq("symbol", PRIMARY).eq("strategy", STRATEGY_ID).eq("mode", "paper")
        .neq("outcome", "open").execute()
    )
    equity = INITIAL_CAPITAL_USD + sum(float(r["pnl_usd"] or 0) for r in closed.data)
    pos = open_trade(client, PRIMARY)
    if pos and eth_last_close and pos.get("entry_actual"):
        mtm = float(pos["size_usd"]) * net_return(float(pos["entry_actual"]), eth_last_close)
        equity += mtm
    return equity


def kill_switch_update(client, equity: float) -> bool:
    """Track peak, compute drawdown, alert on activation. Returns active."""
    peak_state = get_state(client, "equity_peak", {"peak": INITIAL_CAPITAL_USD})
    peak = max(float(peak_state["peak"]), equity)
    set_state(client, "equity_peak", {"peak": peak})

    kill = get_state(client, "kill_switch", {"active": False})
    dd = (peak - equity) / peak if peak > 0 else 0.0
    if not kill.get("active") and dd >= KILL_SWITCH_DD:
        kill = {
            "active": True,
            "since": datetime.now(timezone.utc).isoformat(),
            "equity": round(equity, 2), "peak": round(peak, 2),
            "drawdown_pct": round(dd * 100, 2),
        }
        set_state(client, "kill_switch", kill)
        tg_send(
            "KILL SWITCH ACTIVATED\n"
            f"Paper equity ${equity:.2f} is {dd * 100:.1f}% below peak ${peak:.2f} "
            f"(limit {KILL_SWITCH_DD * 100:.0f}%).\n"
            "New entries are halted; open positions still get exit signals.\n"
            "Manual reset only - see README (engine_state.kill_switch)."
        )
    return bool(get_state(client, "kill_switch", {"active": False}).get("active"))


# --------------------------------------------------------------- signal I/O

def upsert_signal(client, row: dict) -> dict | None:
    """Insert unless (strategy, symbol, bar, type) exists. Returns the row
    if newly inserted, None if it already existed (idempotent re-run)."""
    res = client.table("signals").upsert(
        row, on_conflict="strategy,symbol,bar_open_time,signal_type",
        ignore_duplicates=True,
    ).execute()
    return res.data[0] if res.data else None


def pending_exit_exists(client, trade_id: int) -> bool:
    res = (
        client.table("signals").select("id")
        .eq("trade_id", trade_id).eq("signal_type", "exit").eq("status", "pending")
        .limit(1).execute()
    )
    return bool(res.data)


def retry_unsent(client) -> None:
    """Signals whose Telegram send failed earlier: retry, oldest first."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    res = (
        client.table("signals").select("id, symbol, signal_type, reasoning")
        .eq("strategy", STRATEGY_ID).eq("telegram_sent", False)
        .gte("created_at", cutoff).order("created_at").limit(10).execute()
    )
    for s in res.data:
        ok = tg_send(f"(resend) {s['symbol']} {s['signal_type']} signal:\n{s['reasoning']}")
        if ok:
            client.table("signals").update({"telegram_sent": True}).eq("id", s["id"]).execute()


# ----------------------------------------------------- observational fills

def fill_observational(client, df) -> None:
    """BTC only: fill pending signals at the open of the bar AFTER the
    signal bar, once that bar exists. ETH is never auto-filled."""
    last_open = df.index[-1]
    res = (
        client.table("signals").select("*")
        .eq("strategy", STRATEGY_ID).eq("symbol", OBSERVATIONAL).eq("status", "pending")
        .order("bar_open_time").execute()
    )
    for sig in res.data:
        import pandas as pd

        bar = pd.Timestamp(sig["bar_open_time"]).tz_localize(None)
        if bar >= last_open:
            continue  # next bar not closed yet; fill on a later run
        later = df.index[df.index > bar]
        if len(later) == 0:
            continue
        fill_bar = later[0]
        fill_price = float(df.loc[fill_bar, "Open"])

        if sig["signal_type"] == "entry":
            trade = client.table("trades").insert({
                "signal_id": sig["id"], "mode": "paper", "notes": "observational",
                "symbol": OBSERVATIONAL, "strategy": STRATEGY_ID,
                "opened_at": fill_bar.isoformat(),
                "entry_actual": fill_price,
                "stop_loss": sig["stop_loss"],
                "size_units": sig["size_units"], "size_usd": sig["size_usd"],
                "outcome": "open",
            }).execute()
            client.table("signals").update(
                {"status": "filled", "trade_id": trade.data[0]["id"]}
            ).eq("id", sig["id"]).execute()
            print(f"[BTC obs] entry filled at {fill_price} ({fill_bar})", flush=True)
        else:  # exit
            if not sig.get("trade_id"):
                continue
            t = client.table("trades").select("*").eq("id", sig["trade_id"]).execute().data
            if not t or t[0]["outcome"] != "open":
                client.table("signals").update({"status": "cancelled"}).eq("id", sig["id"]).execute()
                continue
            t = t[0]
            pnl_pct = net_return(float(t["entry_actual"]), fill_price)
            pnl_usd = float(t["size_usd"]) * pnl_pct
            outcome = "win" if pnl_pct > 0 else ("loss" if pnl_pct < 0 else "breakeven")
            client.table("trades").update({
                "closed_at": fill_bar.isoformat(), "exit_actual": fill_price,
                "pnl_pct": pnl_pct, "pnl_usd": pnl_usd, "outcome": outcome,
            }).eq("id", t["id"]).execute()
            client.table("signals").update({"status": "filled"}).eq("id", sig["id"]).execute()
            print(f"[BTC obs] exit filled at {fill_price}, pnl {pnl_pct * 100:+.2f}%", flush=True)


# ------------------------------------------------------------ symbol logic

def process_symbol(client, symbol: str, equity: float, kill_active: bool) -> None:
    import pandas as pd

    df = fetch_recent_4h(symbol, HISTORY_DAYS)
    close = df["Close"].to_numpy()
    n = len(close)
    if n < LOOKBACK_N + 2:
        raise RuntimeError(f"{symbol}: only {n} 4h bars, need {LOOKBACK_N + 2}")

    if symbol == OBSERVATIONAL:
        fill_observational(client, df)

    mom = momentum(close, LOOKBACK_N)
    atr_arr = atr(df["High"].to_numpy(), df["Low"].to_numpy(), close, ATR_N)
    newest_bar = df.index[-1]
    label = "observational" if symbol == OBSERVATIONAL else "primary"

    # Catch-up window: first positional index not yet evaluated by any run.
    # First run after deploy (no marker): evaluate only the newest bar, as
    # before - do not dredge months of history.
    last_eval = get_last_evaluated(client, symbol)
    if last_eval is None:
        start_idx = n - 1
    else:
        after = df.index.searchsorted(last_eval, side="right")
        start_idx = min(max(int(after), 1), n - 1)
    skipped = (n - 1) - start_idx  # bars no run ever looked at

    trade = open_trade(client, symbol)

    if trade:
        stop = float(trade["stop_loss"])
        opened = pd.Timestamp(trade["opened_at"])
        if opened.tzinfo is not None:
            opened = opened.tz_convert("UTC").tz_localize(None)
        # Stop-breach scan across every un-evaluated bar (a skipped run must
        # not skip a stop). Only bars that CLOSED after the trade opened.
        scan = df.iloc[start_idx:]
        scan = scan[scan.index + pd.Timedelta(hours=4) > opened]
        breach = scan[scan["Low"] <= stop]
        stop_hit_bar = breach.index[0] if len(breach) else None
        mom_flip = mom[-1] <= 0  # state-based: any late run still sees it

        if (stop_hit_bar is not None or mom_flip) and not pending_exit_exists(client, trade["id"]):
            if stop_hit_bar is not None:
                reason = "stop hit"
                sig_bar = stop_hit_bar
                ref_price = float(df.loc[stop_hit_bar, "Close"])
                late_note = (
                    f" (breach detected late - occurred on the {myt(stop_hit_bar)} bar; runs were skipped)"
                    if stop_hit_bar != newest_bar else ""
                )
            else:
                reason = "momentum flipped negative"
                sig_bar = newest_bar
                ref_price = float(close[-1])
                late_note = ""
            reasoning = (
                f"EXIT {symbol} ({label}): {reason} on the {myt(sig_bar)} 4h close{late_note}. "
                f"Reference price {ref_price:.2f}, stop was {stop:.2f}. "
                + ("Log your actual exit on the dashboard." if symbol == PRIMARY
                   else "Observational - engine will auto-fill at next bar open.")
            )
            new = upsert_signal(client, {
                "symbol": symbol, "strategy": STRATEGY_ID, "direction": "flat",
                "signal_type": "exit", "bar_open_time": sig_bar.isoformat(),
                "entry_price": ref_price, "stop_loss": stop,
                "reasoning": reasoning, "trade_id": trade["id"],
                "backtest_stats": BACKTEST_STATS[symbol], "status": "pending",
            })
            if new:
                sent = tg_send(
                    (f"EXIT signal - {symbol}\nReason: {reason}{late_note}\nReference: {ref_price:.2f}\n"
                     f"Log your exit on the dashboard.") if symbol == PRIMARY
                    else f"[observational] BTC exit ({reason}) at ref {ref_price:.2f}. No action needed."
                )
                if sent:
                    client.table("signals").update({"telegram_sent": True}).eq("id", new["id"]).execute()
                print(f"[{symbol}] exit signal written ({reason}){late_note}", flush=True)
        set_last_evaluated(client, symbol, newest_bar)
        return

    # No open position. Entry scanning resumes from the most recent exit bar:
    # while the position was open (possibly long past the exit signal, if the
    # fill was logged late) no run looked for entries, so the marker cannot be
    # trusted for this path. Widening to the exit bar is safe by construction -
    # find_live_cross only returns a transition at index >= start that is STILL
    # live, so it cannot resurrect a dead cross, cannot re-enter after a
    # stop-out taken while momentum stayed positive (no transition exists after
    # that exit), and the dedupe index blocks re-notifying a cross already
    # signalled.
    exit_bar = last_exit_bar(client, symbol)
    if exit_bar is not None:
        after_exit = int(df.index.searchsorted(exit_bar, side="right"))
        start_idx = min(start_idx, min(max(after_exit, 1), n - 1))

    cross_idx = find_live_cross(mom, start_idx)
    if cross_idx is None:
        print(f"[{symbol}] no signal at {newest_bar} (mom {mom[-1]:+.4f}, {skipped} caught-up bars)", flush=True)
        set_last_evaluated(client, symbol, newest_bar)
        return
    if kill_active:
        print(f"[{symbol}] entry suppressed by kill switch", flush=True)
        tg_send(f"Entry signal on {symbol} SUPPRESSED - kill switch active.")
        set_last_evaluated(client, symbol, newest_bar)
        return

    # Anchor the signal to the CROSS bar (faithful to what the strategy saw;
    # also makes the dedupe key stable however late we detect it).
    bar_time = df.index[cross_idx]
    price = float(close[cross_idx])
    bars_late = (n - 1) - cross_idx
    late_note = ""
    if bars_late:
        faithful_fill = float(df.iloc[cross_idx + 1]["Open"])
        late_note = (
            f" DETECTED {bars_late} bar(s) LATE (runs were skipped): the faithful next-bar-open "
            f"fill was {faithful_fill:.2f}; current price is {close[-1]:.2f} - log at an "
            f"achievable price, the record keeps both."
        )

    sizing = size_position(equity, price, float(atr_arr[cross_idx]))
    if sizing is None:
        set_last_evaluated(client, symbol, newest_bar)
        return
    stop, risk_usd = sizing["stop"], sizing["risk_usd"]
    units, size_usd = sizing["units"], sizing["size_usd"]
    a = float(atr_arr[cross_idx])

    stats = BACKTEST_STATS[symbol]
    reasoning = (
        f"ENTRY {symbol} long ({label}): 30-day momentum crossed positive at the "
        f"{myt(bar_time)} 4h close ({mom[cross_idx] * 100:+.2f}% vs 30 days ago). "
        f"Reference entry {price:.2f}; stop {stop:.2f} (2x ATR14 = {ATR_MULT * a:.2f}); "
        f"size {units:.6f} {symbol[:-4]} = ${size_usd:.2f} "
        f"(~RM{size_usd * MYR_PER_USD:.0f} display) risking ${risk_usd:.2f} "
        f"(1% of ${equity:.2f} paper equity). "
        f"Backtest context ({stats['window']}, {stats['trades']} trades): "
        f"{stats['expectancy_pct_after_fees']:+.2f}%/trade after fees, "
        f"{stats['win_rate_pct']:.0f}% win rate, avg win {stats['avg_win_pct']:+.1f}% "
        f"vs avg loss {stats['avg_loss_pct']:+.1f}%." + late_note
    )
    new = upsert_signal(client, {
        "symbol": symbol, "strategy": STRATEGY_ID, "direction": "long",
        "signal_type": "entry", "bar_open_time": bar_time.isoformat(),
        "entry_price": price, "stop_loss": stop,
        "size_units": units, "size_usd": size_usd,
        "position_size_pct": size_usd / equity * 100,
        "reasoning": reasoning, "backtest_stats": stats, "status": "pending",
    })
    if new:
        sent = tg_send(
            (f"ENTRY signal - {symbol} LONG\nReference: {price:.2f}\nStop: {stop:.2f}\n"
             f"Size: {units:.6f} {symbol[:-4]} = ${size_usd:.2f} (~RM{size_usd * MYR_PER_USD:.0f})\n"
             f"Risk: ${risk_usd:.2f} (1% of equity)\n\n{reasoning}\n\n"
             "Log your fill on the dashboard.") if symbol == PRIMARY
            else f"[observational] BTC entry signal at ref {price:.2f}, stop {stop:.2f}. "
                 "Engine will auto-fill at next bar open. No action needed."
        )
        if sent:
            client.table("signals").update({"telegram_sent": True}).eq("id", new["id"]).execute()
        print(f"[{symbol}] entry signal written at {price}"
              + (f" ({bars_late} bars late)" if bars_late else ""), flush=True)
    set_last_evaluated(client, symbol, newest_bar)


def heartbeat(client, equity: float, kill_active: bool) -> None:
    """One heartbeat per UTC day, sent by the FIRST engine run that fires
    that day. Normally that's the 00:xx UTC slot (~08:09 MYT); if GitHub
    skips it, the next slot to fire carries it instead. Skip-proof: as long
    as ANY run fires that day you get one 'engine alive' message, so silence
    for a whole day means the engine genuinely did not run (not just a
    skipped morning slot). Only marks the day done on a successful send, so
    a Telegram failure retries on the next run."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if get_state(client, "last_heartbeat_date", {"date": None}).get("date") == today:
        return
    peak = float(get_state(client, "equity_peak", {"peak": INITIAL_CAPITAL_USD})["peak"])
    dd = (peak - equity) / peak * 100 if peak > 0 else 0.0
    pos = open_trade(client, PRIMARY)
    pos_txt = (
        f"open ETH position: entry {pos['entry_actual']}, stop {pos['stop_loss']}"
        if pos else "no open ETH position"
    )
    sent = tg_send(
        f"Heartbeat - engine alive\n"
        f"Paper equity: ${equity:.2f} (~RM{equity * MYR_PER_USD:.0f}) | peak ${peak:.2f} "
        f"| drawdown {dd:.1f}% (kill at {KILL_SWITCH_DD * 100:.0f}%)\n"
        f"{pos_txt}\nKill switch: {'ACTIVE' if kill_active else 'off'}"
    )
    if sent:
        set_state(client, "last_heartbeat_date", {"date": today})


def main() -> None:
    client = get_supabase()

    # Friendly guard: migration 003 must be applied.
    try:
        client.table("signals").select("signal_type").limit(1).execute()
        client.table("engine_state").select("key").limit(1).execute()
    except Exception:
        print("ERROR: schema missing Phase 2 columns - run db/migrations/003_paper_trading.sql "
              "in the Supabase SQL editor first.", file=sys.stderr)
        sys.exit(1)

    failures = []
    eth_close = None
    try:
        eth_df = fetch_recent_4h(PRIMARY, HISTORY_DAYS)
        eth_close = float(eth_df["Close"].iloc[-1])
    except Exception as exc:
        failures.append(f"{PRIMARY} fetch: {exc}")

    equity = eth_equity(client, eth_close)
    kill_active = kill_switch_update(client, equity)
    print(f"paper equity ${equity:.2f} | kill {'ACTIVE' if kill_active else 'off'}", flush=True)

    for symbol in (PRIMARY, OBSERVATIONAL):
        try:
            process_symbol(client, symbol, equity, kill_active)
        except Exception as exc:  # noqa: BLE001
            print(f"[{symbol}] FAILED: {exc}", file=sys.stderr)
            failures.append(f"{symbol}: {exc}")

    try:
        retry_unsent(client)
        heartbeat(client, equity, kill_active)
    except Exception as exc:  # noqa: BLE001
        print(f"post-processing FAILED: {exc}", file=sys.stderr)
        failures.append(str(exc))

    if failures:
        print("Engine failed for: " + "; ".join(failures), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
