"""Verify candle data: row counts, date range, and gap detection (Phase 0).

Per symbol/timeframe, prints row count, earliest/latest open_time, and any
gaps found by comparing consecutive open_time values against the expected
interval. Gaps are reported, not fatal: Binance has rare legitimate gaps
(exchange maintenance). Each gap comes with the exact backfill.py command
to attempt a re-fetch - if that returns nothing, the gap is Binance-side.

    python scripts/verify.py
"""

from candle_lib import (
    INTERVAL_MS,
    SYMBOLS,
    TIMEFRAMES,
    get_supabase,
    iso_to_ms,
    ms_to_iso,
)

PAGE = 1000  # Supabase caps rows per request at 1000 by default


def fetch_all_open_times(client, symbol: str, timeframe: str) -> list[int]:
    """All open_times (epoch ms, ascending) for one symbol/timeframe."""
    out: list[int] = []
    offset = 0
    while True:
        res = (
            client.table("candles")
            .select("open_time")
            .eq("symbol", symbol)
            .eq("timeframe", timeframe)
            .order("open_time")
            .range(offset, offset + PAGE - 1)
            .execute()
        )
        if not res.data:
            break
        out.extend(iso_to_ms(r["open_time"]) for r in res.data)
        offset += len(res.data)
    return out


def main() -> None:
    client = get_supabase()
    total_gaps = 0

    for symbol in SYMBOLS:
        for timeframe in TIMEFRAMES:
            times = fetch_all_open_times(client, symbol, timeframe)
            if not times:
                print(f"[{symbol} {timeframe}] 0 rows - run scripts/backfill.py")
                continue

            print(
                f"[{symbol} {timeframe}] rows={len(times)} "
                f"earliest={ms_to_iso(times[0])} latest={ms_to_iso(times[-1])}"
            )

            interval = INTERVAL_MS[timeframe]
            gaps = [
                (prev + interval, cur - interval)  # first..last missing open_time
                for prev, cur in zip(times, times[1:])
                if cur - prev > interval
            ]
            for first_missing, last_missing in gaps:
                n_missing = (last_missing - first_missing) // interval + 1
                print(
                    f"  GAP: {n_missing} missing candle(s) "
                    f"{ms_to_iso(first_missing)} .. {ms_to_iso(last_missing)}"
                )
                print(
                    f"       re-fetch: python scripts/backfill.py"
                    f" --symbol {symbol} --timeframe {timeframe}"
                    f" --start {ms_to_iso(first_missing)} --end {ms_to_iso(last_missing)}"
                )
            if gaps:
                total_gaps += len(gaps)
            else:
                print("  no gaps")

    if total_gaps:
        print(
            f"\n{total_gaps} gap(s) found. If a re-fetch returns nothing, the gap is "
            "on Binance's side (exchange maintenance) and can be left as-is."
        )
    else:
        print("\nAll symbol/timeframe pairs are gap-free.")


if __name__ == "__main__":
    main()
