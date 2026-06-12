"""Load candles from Supabase into backtesting.py-ready DataFrames.

Full history per symbol/timeframe is cached to backtest/data/*.parquet
(gitignored); the requested window is sliced in memory, so the cache stays
window-independent. Reading uses the anon key when available (RLS allows
SELECT on candles) and falls back to the service role key - both are local
env values, never committed.
"""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(__file__).resolve().parent / "data"
PAGE = 1000  # Supabase caps rows per request

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    load_dotenv(REPO_ROOT / ".env")
    load_dotenv(REPO_ROOT / "dashboard" / ".env.local")
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = (
        os.environ.get("SUPABASE_ANON_KEY")
        or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    )
    if not url or not key:
        raise RuntimeError(
            "No Supabase credentials found (.env or dashboard/.env.local)."
        )
    _client = create_client(url, key)
    return _client


def _fetch_all(symbol: str, timeframe: str) -> pd.DataFrame:
    client = _get_client()
    rows: list[dict] = []
    offset = 0
    while True:
        res = (
            client.table("candles")
            .select("open_time, open, high, low, close, volume")
            .eq("symbol", symbol)
            .eq("timeframe", timeframe)
            .order("open_time")
            .range(offset, offset + PAGE - 1)
            .execute()
        )
        if not res.data:
            break
        rows.extend(res.data)
        offset += len(res.data)

    if not rows:
        raise ValueError(f"No candles in Supabase for {symbol} {timeframe}")

    df = pd.DataFrame(rows)
    # Naive UTC index; backtesting.py prefers tz-naive datetimes.
    df.index = pd.to_datetime(df.pop("open_time"), utc=True).dt.tz_localize(None)
    df.index.name = "Time"
    df = df.rename(
        columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"}
    ).astype(float)
    return df[["Open", "High", "Low", "Close", "Volume"]]


def _validate(df: pd.DataFrame, label: str) -> None:
    if df.empty:
        raise ValueError(f"{label}: empty DataFrame")
    if not df.index.is_monotonic_increasing:
        raise ValueError(f"{label}: timestamps not ascending")
    if not df.index.is_unique:
        raise ValueError(f"{label}: duplicate timestamps")
    if df.isna().any().any():
        raise ValueError(f"{label}: NaN values present")


def load_candles(
    symbol: str,
    timeframe: str = "1d",
    start: str | None = None,
    end: str | None = None,
    refresh: bool = False,
) -> pd.DataFrame:
    """OHLCV DataFrame for [start, end] (inclusive), columns capitalized
    as backtesting.py requires. start/end are ISO dates; None = unbounded."""
    cache = DATA_DIR / f"{symbol}_{timeframe}.parquet"

    if cache.exists() and not refresh:
        df = pd.read_parquet(cache)
    else:
        df = _fetch_all(symbol, timeframe)
        DATA_DIR.mkdir(exist_ok=True)
        df.to_parquet(cache)

    _validate(df, f"{symbol} {timeframe}")

    if start is not None:
        df = df[df.index >= pd.Timestamp(start)]
    if end is not None:
        df = df[df.index <= pd.Timestamp(end)]
    if df.empty:
        raise ValueError(f"{symbol} {timeframe}: window {start}..{end} contains no rows")
    return df.copy()
