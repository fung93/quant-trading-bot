-- 001_candles.sql
-- Phase 0: candle history table.
-- Run manually in the Supabase SQL editor (before 002_registry.sql).

create table if not exists candles (
  id bigserial primary key,
  symbol text not null,            -- 'BTCUSDT', 'ETHUSDT'
  timeframe text not null,         -- '1h', '4h', '1d'
  open_time timestamptz not null,
  open numeric,
  high numeric,
  low numeric,
  close numeric,
  volume numeric,
  unique (symbol, timeframe, open_time)
);

-- Fast latest-candle lookups (resume logic, sync window, dashboard freshness).
create index if not exists candles_symbol_timeframe_open_time_desc_idx
  on candles (symbol, timeframe, open_time desc);

-- RLS: the Phase 0.5 dashboard reads candles with the anon key.
-- Ingestion scripts use the service role key, which bypasses RLS.
alter table candles enable row level security;

drop policy if exists "anon read candles" on candles;
create policy "anon read candles"
  on candles
  for select
  to anon
  using (true);
