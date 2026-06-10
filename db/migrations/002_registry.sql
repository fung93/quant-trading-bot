-- 002_registry.sql
-- Phase 0: schema for strategies, signals, trades. Empty until Phase 2;
-- versioned now so the schema history lives in the repo.
-- Run manually in the Supabase SQL editor, after 001_candles.sql.

create table if not exists strategies (
  id text primary key,             -- 'ma_cross_v1'
  description text,
  params jsonb,
  status text,                     -- 'research' | 'paper' | 'live' | 'retired'
  created_at timestamptz default now()
);

create table if not exists signals (
  id bigserial primary key,
  created_at timestamptz default now(),
  symbol text not null,
  strategy text not null,          -- strategy identifier + version, e.g. 'ma_cross_v1'
  direction text not null,         -- 'long' | 'short' | 'flat'
  entry_price numeric,
  stop_loss numeric,
  take_profit numeric,
  position_size_pct numeric,       -- % of capital
  reasoning text,                  -- plain-language explanation
  backtest_stats jsonb             -- win rate, expectancy, sample size for this setup
);

create table if not exists trades (
  id bigserial primary key,
  signal_id bigint references signals(id),
  mode text not null,              -- 'paper' | 'live'
  opened_at timestamptz,
  closed_at timestamptz,
  entry_actual numeric,
  exit_actual numeric,
  pnl_pct numeric,                 -- after modeled fees
  outcome text,                    -- 'win' | 'loss' | 'breakeven' | 'open'
  notes text
);

-- RLS enabled with no anon policies: deny by default for anon/authenticated.
-- The service role key (server-side only) bypasses RLS.
alter table strategies enable row level security;
alter table signals enable row level security;
alter table trades enable row level security;
