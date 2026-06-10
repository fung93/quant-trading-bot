"""Hourly sync: pull the newest closed candles for each symbol/timeframe.

Runs from GitHub Actions every hour (see .github/workflows/sync-candles.yml).
The fetch window starts at (max open_time in DB - 2 intervals): the overlap
re-upserts the most recent stored candles in case Binance revised them, and
the idempotent upsert makes that safe. Unclosed candles are dropped by
candle_lib.ingest_range, so strategies only ever see closed candles.

Exits non-zero on any failure so GitHub Actions marks the run red. The next
run self-heals: its window always derives from what actually landed in the
table, not from wall-clock time. Errors out (rather than backfilling 5 years
inside a 10-minute CI job) if a symbol/timeframe has no rows yet - run
scripts/backfill.py once first.
"""

import sys

from candle_lib import (
    INTERVAL_MS,
    SYMBOLS,
    TIMEFRAMES,
    get_supabase,
    ingest_range,
    max_open_time_ms,
    ms_to_iso,
)


def main() -> None:
    client = get_supabase()
    failures = []

    for symbol in SYMBOLS:
        for timeframe in TIMEFRAMES:
            try:
                known_max = max_open_time_ms(client, symbol, timeframe)
                if known_max is None:
                    raise RuntimeError(
                        "no rows in candles for this pair - run scripts/backfill.py first"
                    )
                start_ms = known_max - 2 * INTERVAL_MS[timeframe]
                n = ingest_range(client, symbol, timeframe, start_ms)
                print(
                    f"[{symbol} {timeframe}] synced {n} rows from {ms_to_iso(start_ms)}",
                    flush=True,
                )
            except Exception as exc:  # noqa: BLE001 - try every pair, fail at end
                print(f"[{symbol} {timeframe}] FAILED: {exc}", file=sys.stderr)
                failures.append(f"{symbol} {timeframe}")

    if failures:
        print("Sync failed for: " + ", ".join(failures), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
