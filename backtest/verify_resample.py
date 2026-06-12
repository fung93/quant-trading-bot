"""Verify the loader's 1h->4h resample against Binance's native 4h klines.

Phase 1b acceptance check: picks random 4h candles per symbol (plus one bin
that spans a known exchange-outage gap) and compares OHLCV against the
exchange's own 4h aggregation. Run after any loader change:

    python backtest/verify_resample.py
"""

import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import requests

from backtest.loader import load_candles

BINANCE = "https://data-api.binance.vision/api/v3/klines"  # api.binance.com is ISP-blocked here
N_RANDOM = 3
GAP_BIN = "2021-08-13 04:00:00"  # spans 2 missing 1h candles (exchange outage)


def native_4h(symbol: str, open_ms: int) -> list | None:
    r = requests.get(
        BINANCE,
        params={"symbol": symbol, "interval": "4h", "startTime": open_ms, "limit": 1},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    return data[0] if data and int(data[0][0]) == open_ms else None


def main() -> None:
    random.seed()  # genuinely random spot-check each run
    failures = 0
    for symbol in ("BTCUSDT", "ETHUSDT"):
        df = load_candles(symbol, "4h")
        picks = [df.index[random.randrange(len(df))] for _ in range(N_RANDOM)]
        gap_ts = None
        try:
            gap_ts = df.loc[GAP_BIN].name
        except KeyError:
            pass
        if gap_ts is not None:
            picks.append(gap_ts)

        for ts in picks:
            ours = df.loc[ts]
            open_ms = int(ts.value // 1_000_000)
            theirs = native_4h(symbol, open_ms)
            if theirs is None:
                print(f"{symbol} {ts}: NOT FOUND natively - investigate")
                failures += 1
                continue
            checks = {
                "Open": float(theirs[1]),
                "High": float(theirs[2]),
                "Low": float(theirs[3]),
                "Close": float(theirs[4]),
                "Volume": float(theirs[5]),
            }
            diffs = {
                k: (ours[k], v)
                for k, v in checks.items()
                if abs(ours[k] - v) > max(1e-8, abs(v) * 1e-9)
            }
            tag = " (outage-gap bin)" if ts == gap_ts else ""
            if diffs:
                print(f"{symbol} {ts}{tag}: MISMATCH {diffs}")
                failures += 1
            else:
                print(f"{symbol} {ts}{tag}: exact match (O/H/L/C/V)")

    if failures:
        print(f"\n{failures} mismatch(es) - resample is NOT trustworthy yet")
        sys.exit(1)
    print("\nAll sampled 4h candles match Binance's native aggregation.")


if __name__ == "__main__":
    main()
