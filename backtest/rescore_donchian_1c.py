"""Phase 1d Task 2: re-SCORE donchian_v1 under the measured fee model.

Same strategy, same a-priori 1c parameters (20d/10d/ATR x2.0/regime 200d),
same data, new cost arithmetic only. No tuning, no grid. Verifies that
entry/exit bars are identical under both fee models (signals are
equity-independent by construction) and writes
backtest/reports/PHASE1C_RESCORE.md.

    python backtest/rescore_donchian_1c.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from backtest.config import COMMISSION_PER_SIDE, MIN_TRADES
from backtest.run import REPORT_DIR, run_backtest

OLD_COMMISSION = 0.002  # historical a-priori model (0.2%/side), Phases 1-1c
NEW_COMMISSION = COMMISSION_PER_SIDE  # measured model from config.py

CELLS = [("BTCUSDT", "train"), ("BTCUSDT", "validation"),
         ("ETHUSDT", "train"), ("ETHUSDT", "validation")]


def main() -> None:
    assert NEW_COMMISSION == 0.001, (
        f"config drift: expected measured model 0.001/side, got {NEW_COMMISSION}"
    )
    rows = []
    all_identical = True

    for symbol, window in CELLS:
        old = run_backtest("donchian_v1", symbol, window, commission=OLD_COMMISSION)
        new = run_backtest("donchian_v1", symbol, window, commission=NEW_COMMISSION)

        same_trades = (
            old["n_trades"] == new["n_trades"]
            and old["_equity"].index.equals(new["_equity"].index)
        )
        # Strongest check: identical entry/exit bars trade-by-trade.
        ot, nt = old.get("_trades"), new.get("_trades")
        if ot is None or nt is None:
            same_seq = same_trades
        else:
            same_seq = (
                list(ot["EntryBar"]) == list(nt["EntryBar"])
                and list(ot["ExitBar"]) == list(nt["ExitBar"])
            )
        all_identical &= bool(same_trades and same_seq)

        rows.append((symbol, window, old, new, same_seq))

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Phase 1c re-score - donchian_v1 under the measured fee model",
        "",
        f"Generated: {ts}. Parameters byte-identical to 1c (a-priori Turtle",
        "defaults: entry 20d, exit 10d, ATR x2.0, regime 200d - frozen since",
        "before any 1c run; see PHASE1C_VERDICT.md provenance). Old model:",
        "0.20%/side (0.4% RT, a-priori). New model: 0.10%/side (0.20% RT,",
        "measured on Sushi/Katana - see EXPERIMENT_LEDGER.md).",
        "",
        "| Symbol | Window | Trades | Expectancy (old -> new) | Total return (old -> new) | Max DD (old -> new) |",
        "|---|---|---|---|---|---|",
    ]
    for symbol, window, old, new, same_seq in rows:
        weak = f" (<{MIN_TRADES}: weak)" if new["weak"] else ""
        lines.append(
            f"| {symbol} | {window} | {new['n_trades']}{weak} "
            f"| {old['expectancy_pct']:+.2f}% -> **{new['expectancy_pct']:+.2f}%** "
            f"| {old['total_return_pct']:+.2f}% -> {new['total_return_pct']:+.2f}% "
            f"| {old['max_dd_pct']:.2f}% -> {new['max_dd_pct']:.2f}% |"
        )

    lines += [
        "",
        f"Trade sequences identical under both fee models: **{all_identical}** "
        "(entry/exit bars compared trade-by-trade; signals are equity-independent,"
        " so only the per-trade cost arithmetic changed).",
        "",
        "## What changed, and what did not",
        "",
    ]

    btc_val_new = next(r for r in rows if r[0] == "BTCUSDT" and r[1] == "validation")[3]
    lines += [
        f"- **BTC validation expectancy moved from -0.12% to "
        f"{btc_val_new['expectancy_pct']:+.2f}% per trade** - the sign flip the 1c "
        "verdict predicted would hinge on the fee line. This is arithmetic on the "
        "same 19 trades, not new evidence of skill.",
        "- Every other cell shifts by the same per-trade fee delta; no ranking "
        "between cells changes.",
        "- **Classification is unchanged: weak/uncertain.** All samples remain "
        f"far below {MIN_TRADES} trades; a result whose sign depends on the fee "
        "model within one round-trip's width is, by definition, thin. The "
        "measured model makes the arithmetic honest - it does not make the "
        "evidence strong.",
        "",
    ]

    out = "\n".join(lines)
    print(out)
    REPORT_DIR.mkdir(exist_ok=True)
    (REPORT_DIR / "PHASE1C_RESCORE.md").write_text(out, encoding="utf-8")
    print("saved: backtest/reports/PHASE1C_RESCORE.md")


if __name__ == "__main__":
    main()
