"""Shared helpers for candle ingestion and verification.

Used by backfill.py, sync.py, verify.py. All timestamps are UTC; Binance
speaks epoch milliseconds, Supabase stores timestamptz (ISO strings).

Closed-candle rule (BUILD_PLAN / Phase 0): only closed candles may ever be
written. A candle is closed when open_time + interval <= Binance server time,
checked against the server clock (not the local one) so clock skew can never
let a still-forming candle slip in.
"""

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from supabase import Client, create_client

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")  # local runs; no-op in CI

# data-api.binance.vision is Binance's official host for public market data
# (identical /api/v3/klines and /api/v3/time, no API key). It is the default
# because api.binance.com is ISP-blocked in Malaysia, where this runs locally;
# both hosts work from GitHub Actions.
BINANCE_BASE = os.environ.get("BINANCE_BASE_URL", "https://data-api.binance.vision")
SYMBOLS = ["BTCUSDT", "ETHUSDT"]
TIMEFRAMES = ["1h", "1d"]
INTERVAL_MS = {"1h": 3_600_000, "1d": 86_400_000}
DEFAULT_START = "2021-01-01T00:00:00+00:00"  # Phase 1 tunes on 2021-2023
KLINES_LIMIT = 1000      # Binance max per request
BATCH_SIZE = 500         # rows per upsert
REQUEST_SLEEP_S = 0.5    # politeness delay between paginated requests
HTTP_TIMEOUT_S = 30


def get_supabase() -> Client:
    """Service-role client from env vars (.env already loaded at import)."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print(
            "ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set "
            "(GitHub Actions secrets in CI, .env at repo root locally).",
            file=sys.stderr,
        )
        sys.exit(1)
    return create_client(url, key)


def ms_to_iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


def iso_to_ms(s: str) -> int:
    dt = datetime.fromisoformat(s.strip())
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def binance_server_time_ms() -> int:
    r = requests.get(f"{BINANCE_BASE}/api/v3/time", timeout=HTTP_TIMEOUT_S)
    r.raise_for_status()
    return int(r.json()["serverTime"])


def fetch_klines(symbol: str, interval: str, start_ms: int) -> list:
    """One page of klines: [openTime, open, high, low, close, volume, ...]."""
    r = requests.get(
        f"{BINANCE_BASE}/api/v3/klines",
        params={
            "symbol": symbol,
            "interval": interval,
            "startTime": start_ms,
            "limit": KLINES_LIMIT,
        },
        timeout=HTTP_TIMEOUT_S,
    )
    r.raise_for_status()
    return r.json()


def kline_to_row(symbol: str, timeframe: str, k: list) -> dict:
    # Binance sends prices/volume as strings; pass them through so Postgres
    # casts text -> numeric exactly, with no float round-trip.
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "open_time": ms_to_iso(k[0]),
        "open": k[1],
        "high": k[2],
        "low": k[3],
        "close": k[4],
        "volume": k[5],
    }


def max_open_time_ms(client: Client, symbol: str, timeframe: str) -> int | None:
    res = (
        client.table("candles")
        .select("open_time")
        .eq("symbol", symbol)
        .eq("timeframe", timeframe)
        .order("open_time", desc=True)
        .limit(1)
        .execute()
    )
    if res.data:
        return iso_to_ms(res.data[0]["open_time"])
    return None


def ingest_range(
    client: Client,
    symbol: str,
    timeframe: str,
    start_ms: int,
    end_ms: int | None = None,
) -> int:
    """Fetch klines from start_ms and upsert closed candles in batches.

    end_ms is inclusive on open_time (candles opening at or before it).
    Idempotent: on_conflict upsert on (symbol, timeframe, open_time).
    Returns rows upserted.
    """
    interval_ms = INTERVAL_MS[timeframe]
    now_ms = binance_server_time_ms()
    cursor = start_ms
    total = 0

    while cursor <= (end_ms if end_ms is not None else now_ms):
        klines = fetch_klines(symbol, timeframe, cursor)
        if not klines:
            break

        # Closed candles only; respect end_ms when doing a targeted re-fetch.
        rows = [
            kline_to_row(symbol, timeframe, k)
            for k in klines
            if k[0] + interval_ms <= now_ms
            and (end_ms is None or k[0] <= end_ms)
        ]

        for i in range(0, len(rows), BATCH_SIZE):
            batch = rows[i : i + BATCH_SIZE]
            client.table("candles").upsert(
                batch, on_conflict="symbol,timeframe,open_time"
            ).execute()
            total += len(batch)
            print(
                f"[{symbol} {timeframe}] {batch[0]['open_time']} .. "
                f"{batch[-1]['open_time']} upserted {len(batch)} rows",
                flush=True,
            )

        if len(klines) < KLINES_LIMIT:
            break  # reached the present (or end of available history)
        cursor = klines[-1][0] + interval_ms
        time.sleep(REQUEST_SLEEP_S)

    return total
