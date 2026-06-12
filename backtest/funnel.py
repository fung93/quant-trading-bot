"""Entry-funnel report: where do signals die, per symbol and window?

ma_cross family: raw fast/slow cross-ups -> + regime filter -> + volume gate.
donchian_v1:     breakout bars (close > prior 20-day high) -> + regime filter.

    python backtest/funnel.py --strategy donchian_v1
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from backtest.config import SYMBOLS, TRAIN, VALIDATION
from backtest.indicators import prior_high, sma
from backtest.loader import load_candles
from backtest.run import REPORT_DIR, STRATEGY_TIMEFRAME, get_strategy

WINDOWS = {"train": TRAIN, "validation": VALIDATION}


def funnel_ma(symbol: str, timeframe: str, window: tuple, cls) -> tuple[int, int, int]:
    df = load_candles(symbol, timeframe, start=window[0], end=window[1])
    close, vol = df["Close"].to_numpy(), df["Volume"].to_numpy()
    f, s = sma(close, cls.fast_n), sma(close, cls.slow_n)
    r, v = sma(close, cls.regime_n), sma(vol, cls.vol_n)

    prev_f, prev_s = np.roll(f, 1), np.roll(s, 1)
    cross_up = (f > s) & (prev_f <= prev_s)
    cross_up[0] = False
    cross_up &= ~np.isnan(f) & ~np.isnan(prev_s)

    regime = close > r          # NaN-safe: NaN compares False
    vol_ok = vol > v

    return int(cross_up.sum()), int((cross_up & regime).sum()), int((cross_up & regime & vol_ok).sum())


def funnel_donchian(symbol: str, timeframe: str, window: tuple, cls) -> tuple[int, int]:
    from strategies.donchian_v1 import BARS_PER_DAY

    df = load_candles(symbol, timeframe, start=window[0], end=window[1])
    close, high = df["Close"].to_numpy(), df["High"].to_numpy()
    channel = prior_high(high, cls.entry_days * BARS_PER_DAY)
    regime = close > sma(close, cls.regime_days * BARS_PER_DAY)

    breakout = close > channel  # NaN warmup compares False
    return int(breakout.sum()), int((breakout & regime).sum())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strategy", choices=["ma_cross_v1", "ma_cross_v1_4h", "donchian_v1"],
                    default="donchian_v1")
    args = ap.parse_args()

    cls = get_strategy(args.strategy)
    timeframe = STRATEGY_TIMEFRAME[args.strategy]

    if args.strategy == "donchian_v1":
        desc = (f"entry channel {cls.entry_days}d, regime SMA {cls.regime_days}d "
                f"(day-anchored, bars = days x 6)")
        header = "| Symbol | Window | breakout bars (close > prior 20d high) | + regime filter (= entry bars) |"
        sep = "|--------|--------|------------------------------------------|--------------------------------|"
    else:
        desc = (f"fast/slow {cls.fast_n}/{cls.slow_n}, regime SMA({cls.regime_n}), "
                f"volume SMA({cls.vol_n})")
        header = "| Symbol | Window | raw cross-ups | + regime filter | + volume gate (= entries) |"
        sep = "|--------|--------|---------------|-----------------|---------------------------|"

    lines = [
        f"# Entry funnel - {args.strategy} ({timeframe} candles)",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  |  {desc}",
        "",
        header,
        sep,
    ]
    for symbol in SYMBOLS:
        for wname, wdates in WINDOWS.items():
            if args.strategy == "donchian_v1":
                raw, after_regime = funnel_donchian(symbol, timeframe, wdates, cls)
                lines.append(f"| {symbol} | {wname} | {raw} | {after_regime} |")
            else:
                raw, after_regime, after_vol = funnel_ma(symbol, timeframe, wdates, cls)
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
