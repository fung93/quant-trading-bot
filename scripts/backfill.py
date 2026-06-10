"""Backfill BTC/ETH candles from Binance into Supabase (Phase 0).

Default run covers every symbol x timeframe, resuming from the max
open_time already in the table (falls back to 2021-01-01, the start of the
Phase 1 training window). Idempotent: re-running never duplicates rows, and
a second run right after a complete one is near-instant.

Optional flags target an exact range, so verify.py can print a runnable
gap-repair command:

    python scripts/backfill.py
    python scripts/backfill.py --symbol BTCUSDT --timeframe 1h \
        --start 2022-03-05T00:00:00+00:00 --end 2022-03-06T00:00:00+00:00
"""

import argparse
import sys

from candle_lib import (
    DEFAULT_START,
    SYMBOLS,
    TIMEFRAMES,
    get_supabase,
    ingest_range,
    iso_to_ms,
    max_open_time_ms,
    ms_to_iso,
)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--symbol", choices=SYMBOLS, help="limit to one symbol")
    ap.add_argument("--timeframe", choices=TIMEFRAMES, help="limit to one timeframe")
    ap.add_argument("--start", help="ISO timestamp; overrides resume-from-max")
    ap.add_argument("--end", help="ISO timestamp; include candles opening at or before this")
    args = ap.parse_args()

    client = get_supabase()
    symbols = [args.symbol] if args.symbol else SYMBOLS
    timeframes = [args.timeframe] if args.timeframe else TIMEFRAMES
    end_ms = iso_to_ms(args.end) if args.end else None
    failures = []

    for symbol in symbols:
        for timeframe in timeframes:
            try:
                if args.start:
                    start_ms = iso_to_ms(args.start)
                else:
                    # Resume: re-fetch from the newest stored candle; the
                    # upsert makes re-writing it harmless.
                    known_max = max_open_time_ms(client, symbol, timeframe)
                    start_ms = known_max if known_max is not None else iso_to_ms(DEFAULT_START)

                span = f"from {ms_to_iso(start_ms)}"
                if end_ms is not None:
                    span += f" to {ms_to_iso(end_ms)}"
                print(f"[{symbol} {timeframe}] backfilling {span}", flush=True)

                n = ingest_range(client, symbol, timeframe, start_ms, end_ms)
                print(f"[{symbol} {timeframe}] done: {n} rows upserted", flush=True)
            except Exception as exc:  # noqa: BLE001 - report, continue, fail at end
                print(f"[{symbol} {timeframe}] FAILED: {exc}", file=sys.stderr)
                failures.append(f"{symbol} {timeframe}")

    if failures:
        print("Backfill failed for: " + ", ".join(failures), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
