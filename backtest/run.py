"""Backtest runner and report generator (Phase 1 Task 5).

    python backtest/run.py --strategy ma_cross_v1 --symbol BTCUSDT --window train
    python backtest/run.py --strategy rsi_revert_v1 --symbol ETHUSDT --window validation

Writes backtest/reports/{strategy}_{symbol}_{window}.md plus an equity-curve
PNG, and prints the same summary. --no-fees exists ONLY for the acceptance
check that fees are really applied; never use it for evaluation.
"""

import argparse
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from backtesting import Backtest

from backtest.benchmark import buy_and_hold
from backtest.config import (
    CASH,
    COMMISSION_PER_SIDE,
    MIN_TRADES,
    TRAIN,
    VALIDATION,
)
from backtest.loader import load_candles

warnings.filterwarnings("ignore", module="backtesting")

REPORT_DIR = Path(__file__).resolve().parent / "reports"

STRATEGIES = {
    "ma_cross_v1": ("strategies.ma_cross_v1", "MaCrossV1"),
    "rsi_revert_v1": ("strategies.rsi_revert_v1", "RsiRevertV1"),
    "ma_cross_v1_4h": ("strategies.ma_cross_v1_4h", "MaCrossV1_4h"),
    "donchian_v1": ("strategies.donchian_v1", "DonchianV1"),
    "tsmom_v1": ("strategies.tsmom_v1", "TsmomV1"),
}
WINDOWS = {"train": TRAIN, "validation": VALIDATION, "full": (None, None)}

# Decision timeframe per strategy version.
STRATEGY_TIMEFRAME = {
    "ma_cross_v1": "1d",
    "rsi_revert_v1": "1d",
    "ma_cross_v1_4h": "4h",
    "donchian_v1": "4h",
    "tsmom_v1": "4h",
}

PARAM_NAMES = {
    "ma_cross_v1": ["fast_n", "slow_n", "regime_n", "atr_mult", "vol_n", "atr_n", "risk_pct"],
    "rsi_revert_v1": ["rsi_n", "entry_th", "exit_th", "regime_n", "atr_mult", "atr_n", "risk_pct"],
    "ma_cross_v1_4h": ["fast_n", "slow_n", "regime_n", "atr_mult", "vol_n", "atr_n", "risk_pct"],
    "donchian_v1": ["entry_days", "exit_days", "regime_days", "atr_mult", "atr_n", "risk_pct"],
    "tsmom_v1": ["lookback_days", "atr_mult", "atr_n", "risk_pct"],
}


def get_strategy(name: str):
    module_name, class_name = STRATEGIES[name]
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)


def run_backtest(
    strategy: str,
    symbol: str,
    window: str,
    commission: float = COMMISSION_PER_SIDE,
    params: dict | None = None,
) -> dict:
    """Run one backtest and return a metrics dict (shared with robustness.py)."""
    start, end = WINDOWS[window]
    timeframe = STRATEGY_TIMEFRAME[strategy]
    df = load_candles(symbol, timeframe, start=start, end=end)
    cls = get_strategy(strategy)

    bt = Backtest(df, cls, cash=CASH, commission=commission, finalize_trades=True)
    stats = bt.run(**(params or {}))
    trades = stats["_trades"]
    equity = stats["_equity_curve"]["Equity"]

    n = len(trades)
    wins = trades[trades["ReturnPct"] > 0]["ReturnPct"]
    losses = trades[trades["ReturnPct"] <= 0]["ReturnPct"]
    days = max((df.index[-1] - df.index[0]).days, 1)

    used_params = {p: (params or {}).get(p, getattr(cls, p)) for p in PARAM_NAMES[strategy]}

    return {
        "strategy": strategy,
        "symbol": symbol,
        "window": window,
        "window_dates": (str(df.index[0].date()), str(df.index[-1].date())),
        "params": used_params,
        "commission": commission,
        "n_trades": n,
        "weak": n < MIN_TRADES,
        "win_rate": len(wins) / n if n else float("nan"),
        "avg_win_pct": wins.mean() * 100 if len(wins) else float("nan"),
        "avg_loss_pct": losses.mean() * 100 if len(losses) else float("nan"),
        "expectancy_pct": trades["ReturnPct"].mean() * 100 if n else float("nan"),
        "total_return_pct": float(stats["Return [%]"]),
        "max_dd_pct": float(stats["Max. Drawdown [%]"]),
        "cagr_pct": ((equity.iloc[-1] / equity.iloc[0]) ** (365.25 / days) - 1) * 100,
        "exposure_pct": float(stats["Exposure Time [%]"]),
        "hodl": buy_and_hold(df),
        "_equity": equity,
        "_close": df["Close"],
    }


def format_report(r: dict) -> str:
    weak_flag = (
        f" **[STATISTICALLY WEAK: {r['n_trades']} trades < {MIN_TRADES}]**" if r["weak"] else ""
    )
    h = r["hodl"]
    fee_note = "" if r["commission"] else "\n> **WARNING: fees disabled - verification run only, not evidence.**\n"
    pct = lambda x: "n/a" if x != x else f"{x:.2f}%"  # NaN-safe

    lines = [
        f"# {r['strategy']} - {r['symbol']} - {r['window']} window",
        "",
        f"Window: {r['window_dates'][0]} -> {r['window_dates'][1]}  |  "
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        fee_note,
        "## Headline",
        "",
        f"- **Expectancy per trade (after fees): {pct(r['expectancy_pct'])}**{weak_flag}",
        f"- Trades: {r['n_trades']}" + (f" (below {MIN_TRADES} - every metric here is weak evidence)" if r["weak"] else ""),
        f"- Win rate: {pct(r['win_rate'] * 100)}  |  Avg win: {pct(r['avg_win_pct'])}  |  Avg loss: {pct(r['avg_loss_pct'])}",
        "",
        "## Risk and return",
        "",
        f"- Strategy total return: {pct(r['total_return_pct'])}  |  CAGR: {pct(r['cagr_pct'])}",
        f"- Max drawdown: {pct(r['max_dd_pct'])}",
        f"- Time in market: {pct(r['exposure_pct'])}",
        "",
        "## vs Buy & Hold (same window)",
        "",
        f"- HODL total return: {h['total_return'] * 100:.2f}%  |  CAGR: {h['cagr'] * 100:.2f}%  |  Max drawdown: {h['max_dd'] * 100:.2f}%",
        f"- Strategy return {pct(r['total_return_pct'])} vs HODL {h['total_return'] * 100:.2f}%; "
        f"strategy drawdown {pct(r['max_dd_pct'])} vs HODL {h['max_dd'] * 100:.2f}%",
        "",
        "## Parameters",
        "",
        f"- Fees: {r['commission']:.4f} per side (fee + slippage), applied on entry and exit",
    ]
    for k, v in r["params"].items():
        lines.append(f"- {k}: {v}")
    lines += [
        "",
        "_Entries fill at the next candle's open; signals use closed candles only "
        "(no lookahead). Stops anchored to the signal close. Sizing: stop-out loses "
        "1% of equity, capped at 99% (spot, no leverage). Whole-unit sizing is "
        "negligible at cash=1e8. The window's first regime_n bars are indicator warmup._",
        "",
    ]
    return "\n".join(lines)


def save_equity_png(r: dict, path: Path) -> None:
    eq = r["_equity"] / r["_equity"].iloc[0]
    hodl = r["_close"] / r["_close"].iloc[0]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(eq.index, eq.values, label=f"{r['strategy']} (after fees)", linewidth=1.4)
    ax.plot(hodl.index, hodl.values, label="Buy & hold", linewidth=1.0, alpha=0.7)
    ax.set_title(f"{r['strategy']} - {r['symbol']} - {r['window']}")
    ax.set_ylabel("Growth of 1.0")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strategy", required=True, choices=sorted(STRATEGIES))
    ap.add_argument("--symbol", required=True, choices=["BTCUSDT", "ETHUSDT"])
    ap.add_argument("--window", required=True, choices=sorted(WINDOWS))
    ap.add_argument("--no-fees", action="store_true",
                    help="verification only: prove fees change results")
    args = ap.parse_args()

    commission = 0.0 if args.no_fees else COMMISSION_PER_SIDE
    r = run_backtest(args.strategy, args.symbol, args.window, commission=commission)

    report = format_report(r)
    print(report)

    REPORT_DIR.mkdir(exist_ok=True)
    suffix = "_nofees" if args.no_fees else ""
    base = f"{args.strategy}_{args.symbol}_{args.window}{suffix}"
    (REPORT_DIR / f"{base}.md").write_text(report, encoding="utf-8")
    save_equity_png(r, REPORT_DIR / f"{base}.png")
    print(f"saved: backtest/reports/{base}.md and .png")


if __name__ == "__main__":
    main()
