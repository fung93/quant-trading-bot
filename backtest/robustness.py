"""Robustness grid for the ma_cross family (anti-overfitting check).

TRAINING window only. Runs a small parameter grid and prints expectancy per
combination. Purpose: see whether results are stable across a *range* of
parameters or a spike at one magic combination (an overfitting warning, not
a discovery). Deliberately does NOT auto-select a winner - the table is for
human judgment.

    python backtest/robustness.py                              # ma_cross_v1 (1d)
    python backtest/robustness.py --strategy ma_cross_v1_4h    # Phase 1b (4h)
    python backtest/robustness.py --strategy donchian_v1       # Phase 1c (4h)
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from backtest.config import MIN_TRADES, SYMBOLS, TRAIN
from backtest.run import REPORT_DIR, run_backtest

MA_GRID = [(10, 50), (20, 50), (20, 100), (50, 200)]
DONCHIAN_ENTRY_GRID = [10, 20, 55]  # days; exit = round(entry / 2)
ATR_GRID = [1.5, 2.0, 3.0]
GRID_STRATEGIES = ["ma_cross_v1", "ma_cross_v1_4h", "donchian_v1"]


def grid_cells(strategy: str) -> tuple[str, list[tuple[str, dict]]]:
    """(combo-column header, [(combo label, params), ...]) for one strategy."""
    if strategy == "donchian_v1":
        cells = [
            (f"{entry}d/{round(entry / 2)}d", {"entry_days": entry, "exit_days": round(entry / 2)})
            for entry in DONCHIAN_ENTRY_GRID
        ]
        return "entry/exit", cells
    cells = [(f"{fast}/{slow}", {"fast_n": fast, "slow_n": slow}) for fast, slow in MA_GRID]
    return "fast/slow", cells


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strategy", choices=GRID_STRATEGIES, default="ma_cross_v1")
    args = ap.parse_args()
    strategy = args.strategy

    lines = [
        f"# Robustness grid - {strategy} - TRAINING window only",
        "",
        f"Window: {TRAIN[0]} -> {TRAIN[1]}  |  Generated: "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "Read this for *stability*, not for a winner. If only one combination",
        "shows positive expectancy, that is an overfitting warning. No",
        "combination is auto-selected.",
        "",
    ]

    combo_header, combos = grid_cells(strategy)

    for symbol in SYMBOLS:
        lines += [
            f"## {symbol}",
            "",
            f"| {combo_header} | ATR x | trades | expectancy/trade | total return | max DD |",
            "|-----------|-------|--------|------------------|--------------|--------|",
        ]
        positives = 0
        cells = 0
        for label, combo_params in combos:
            for atr_mult in ATR_GRID:
                r = run_backtest(
                    strategy,
                    symbol,
                    "train",
                    params={**combo_params, "atr_mult": atr_mult},
                )
                cells += 1
                exp = r["expectancy_pct"]
                if exp == exp and exp > 0:  # NaN-safe
                    positives += 1
                weak = f" (<{MIN_TRADES}: weak)" if r["weak"] else ""
                exp_s = "n/a (0 trades)" if exp != exp else f"{exp:+.2f}%"
                lines.append(
                    f"| {label} | {atr_mult} | {r['n_trades']}{weak} "
                    f"| {exp_s} | {r['total_return_pct']:+.2f}% | {r['max_dd_pct']:.2f}% |"
                )
        lines += [
            "",
            f"Positive-expectancy cells: {positives}/{cells}.",
            "",
        ]

    lines += [
        "## How to read this",
        "",
        "- Stable edge: most cells positive, similar magnitudes -> parameters",
        "  are not doing the heavy lifting.",
        "- One hot cell amid noise: overfitting warning - the 'edge' is the",
        "  parameter choice, not the market behavior.",
        "- All trade counts here are far below 30: every number on this page",
        "  is statistically weak evidence either way.",
        "",
    ]

    out = "\n".join(lines)
    print(out)
    REPORT_DIR.mkdir(exist_ok=True)
    (REPORT_DIR / f"robustness_{strategy}.md").write_text(out, encoding="utf-8")
    print(f"saved: backtest/reports/robustness_{strategy}.md")


if __name__ == "__main__":
    main()
