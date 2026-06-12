-- 003_paper_trading.sql
-- Phase 2: signal engine + paper trading columns, engine state, RLS for the
-- dashboard's read paths, and tsmom_v1 registration.
-- Run manually in the Supabase SQL editor, after 001 and 002.

-- Signals gain typing, idempotency key, sizing and delivery bookkeeping.
alter table signals
  add column if not exists signal_type text not null default 'entry',   -- 'entry' | 'exit'
  add column if not exists bar_open_time timestamptz,                   -- the closed 4h bar evaluated
  add column if not exists size_units numeric,                          -- position size in coin
  add column if not exists size_usd numeric,                            -- position size in USD
  add column if not exists status text not null default 'pending',      -- 'pending' | 'filled' | 'cancelled'
  add column if not exists trade_id bigint references trades(id),       -- exit signals reference the open trade
  add column if not exists telegram_sent boolean not null default false;

-- Idempotency: one signal per (strategy, symbol, bar, type) - re-runs and
-- overlapping crons upsert into this and cannot duplicate.
create unique index if not exists signals_dedupe_idx
  on signals (strategy, symbol, bar_open_time, signal_type);

-- Trades gain direct columns so the engine can query open positions without
-- joins, plus USD PnL for equity arithmetic.
alter table trades
  add column if not exists symbol text,
  add column if not exists strategy text,
  add column if not exists stop_loss numeric,
  add column if not exists size_units numeric,
  add column if not exists size_usd numeric,
  add column if not exists pnl_usd numeric;

-- Engine state: kill switch, equity peak. Key/value keeps it schema-light.
create table if not exists engine_state (
  key text primary key,
  value jsonb not null,
  updated_at timestamptz not null default now()
);
alter table engine_state enable row level security;

-- Phase 2 dashboard reads signals/trades/engine_state with the anon key
-- (owner's own paper records; all writes stay behind the PIN-gated API
-- route that uses the service role key server-side).
drop policy if exists "anon read signals" on signals;
create policy "anon read signals" on signals for select to anon using (true);
drop policy if exists "anon read trades" on trades;
create policy "anon read trades" on trades for select to anon using (true);
drop policy if exists "anon read engine_state" on engine_state;
create policy "anon read engine_state" on engine_state for select to anon using (true);

-- Register the promoted strategy (immutable from here on).
insert into strategies (id, description, params, status)
values (
  'tsmom_v1',
  'Time-series momentum: 30d lookback on 4h candles, long-only, ATR(14)x2 hard stop, 1% risk sizing. Promoted from Phase 1d - first validated cell (ETH validation +1.63%/trade after measured fees, 80 trades).',
  '{"lookback_days": 30, "atr_mult": 2.0, "atr_n": 14, "risk_pct": 0.01, "timeframe": "4h"}'::jsonb,
  'paper'
)
on conflict (id) do nothing;
