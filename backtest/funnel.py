"""Entry-funnel report for the ma_cross family (Phase 1b Task 3).

Counts, per symbol and window: raw fast/slow cross-ups -> survivors of the
regime filter -> survivors of the volume gate. Sample starvation was the
Phase 1 diagnosis; this measures exactly where signals die.

    python backtest/funnel.py --strategy ma_cross_v1_4h
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from backtest.config import SYMBOLS, TRAIN, VALIDATION
from backtest.indicators import sma
from backtest.loader import load_candles
from backtest.run import REPORT_DIR, STRATEGY_TIMEFRAME, get_strategy

WINDOWS = {"train": TRAIN, "validation": VALIDATION}


def funnel(symbol: str, timeframe: str, window: tuple, fast_n: int, slow_n: int,
           regime_n: int, vol_n: int) -> tuple[int, int, int]:
    df = load_candles(symbol, timeframe, start=window[0], end=window[1])
    close, vol = df["Close"].to_numpy(), df["Volume"].to_numpy()
    f, s = sma(close, fast_n), sma(close, slow_n)
    r, v = sma(close, regime_n), sma(vol, vol_n)

    prev_f, prev_s = np.roll(f, 1), np.roll(s, 1)
    cross_up = (f > s) & (prev_f <= prev_s)
    cross_up[0] = False
    cross_up &= ~np.isnan(f) & ~np.isnan(prev_s)

    regime = close > r          # NaN-safe: NaN compares False
    vol_ok = vol > v

    return int(cross_up.sum()), int((cross_up & regime).sum()), int((cross_up & regime & vol_ok).sum())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strategy", choices=["ma_cross_v1", "ma_cross_v1_4h"],
                    default="ma_cross_v1_4h")
    args = ap.parse_args()

    cls = get_strategy(args.strategy)
    timeframe = STRATEGY_TIMEFRAME[args.strategy]

    lines = [
        f"# Entry funnel - {args.strategy} ({timeframe} candles)",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  |  "
        f"fast/slow {cls.fast_n}/{cls.slow_n}, regime SMA({cls.regime_n}), "
        f"volume SMA({cls.vol_n})",
        "",
        "| Symbol | Window | raw cross-ups | + regime filter | + volume gate (= entries) |",
        "|--------|--------|---------------|-----------------|---------------------------|",
    ]
    for symbol in SYMBOLS:
        for wname, wdates in WINDOWS.items():
            raw, after_regime, after_vol = funnel(
                symbol, timeframe, wdates, cls.fast_n, cls.slow_n, cls.regime_n, cls.vol_n
            )
            lines.append(f"| {symbol} | {wname} | {raw} | {after_regime} | {after_vol} |")

    lines += [
        "",
        "_Entries can be slightly fewer than the last column in a backtest:"
        " a signal is skipped when a position is already open._",
        "",
    ]
    out = "\n".join(lines)
    print(out)
    REPORT_DIR.mkdir(exist_ok=True)
    (REPORT_DIR / f"funnel_{args.strategy}.md").write_text(out, encoding="utf-8")
    print(f"saved: backtest/reports/funnel_{args.strategy}.md")


if __name__ == "__main__":
    main()
