# Quant Trading Bot — Build Plan

## Project Overview

A personal quantitative trading system for BTC and ETH, built in phases from manual paper trading to small-scale on-chain automation. Primary objective in early phases is **learning**, not profit. Everything must run on free tiers.

**Owner:** Nicholas (solo developer, Malaysia-based, self-directed investor)
**Stack philosophy:** Same stack pattern as the owner's other projects (Next.js/Vercel, Supabase, GitHub Actions), but built fresh. Minimal infrastructure.

**IMPORTANT — Project isolation:** This is a standalone project. It is completely separate from the owner's Tiger Foundation Dashboard: separate repo, separate Supabase project, separate Vercel deployment, separate credentials. Never reference, import from, modify, or assume anything about the Tiger Foundation Dashboard. Nothing is shared between the two projects.

## Repo Structure (monorepo)

```
quant-bot/
├── BUILD_PLAN.md
├── CLAUDE.md
├── README.md
├── requirements.txt
├── .env.example
├── db/migrations/        # SQL, run manually in Supabase SQL editor
├── scripts/              # Python: backfill, sync, verify, signal engine
├── strategies/           # one file per strategy version, immutable once in paper mode
├── backtest/             # Phase 1 local backtesting lab
├── .github/workflows/    # cron jobs
└── dashboard/            # Next.js app (Vercel root directory = dashboard/)
```

Vercel project is configured with `dashboard/` as the root directory so only dashboard changes trigger deploys.

## Architecture

```
Binance public API ──┐
Coinalyze (optional) ─┼──> GitHub Actions cron ──> Supabase (Postgres, dedicated project)
CoinGecko (optional) ─┘            │                     │
                                   │                     ├──> dashboard/ on Vercel (anon key + RLS)
                       Signal engine (daily cron)        ├──> Telegram bot (notifications)
                                   │                     │
                       Local backtesting lab ────────────┘
                       (Python, WSL2, backtesting.py/vectorbt)

Phase 4 only: Signal engine ──> execution module ──> hot wallet ──> DEX (Sushi/Katana)
```

## Core Principles (apply to all phases)

1. **Free tier only.** Binance public market data endpoints (no API key for market data), Supabase free tier, GitHub Actions free minutes, Vercel Hobby, Telegram Bot API.
2. **Expectancy over win rate.** All strategy evaluation uses: expectancy = (win% × avg win) − (loss% × avg loss), after fees. Also track max drawdown and trade count. Never optimize for win rate alone.
3. **Fees are always modeled.** Backtests and paper trades assume 0.1% fee + 0.1% slippage per side (0.4% round trip) unless measured otherwise.
4. **Out-of-sample discipline.** Strategies are tuned on a training window and validated on unseen data. A strategy that only works in-sample is rejected.
5. **Risk first.** Max 1–2% of capital at risk per trade. Position size derived from stop-loss distance, not gut feel.
6. **No automation without a gate.** Live execution (Phase 4) requires 3–6 months of positive-expectancy paper trading through at least one drawdown.
7. **Every signal carries reasoning.** Signals are stored with a plain-language explanation (ELI5 style) of why the trade was generated and the historical stats behind the setup.

## Database Schema (Supabase)

```sql
-- Candle history
candles (
  id bigserial primary key,
  symbol text not null,            -- 'BTCUSDT', 'ETHUSDT'
  timeframe text not null,         -- '1h', '4h', '1d'
  open_time timestamptz not null,
  open numeric, high numeric, low numeric, close numeric,
  volume numeric,
  unique (symbol, timeframe, open_time)
);

-- Generated signals
signals (
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

-- Paper/live trade log
trades (
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

-- Strategy registry
strategies (
  id text primary key,             -- 'ma_cross_v1'
  description text,
  params jsonb,
  status text,                     -- 'research' | 'paper' | 'live' | 'retired'
  created_at timestamptz default now()
);
```

## Phase 0 — Data Foundation

**Goal:** BTC/ETH candle data flowing into Supabase automatically, with full historical backfill.

**Deliverables:**
- Supabase tables created (schema above)
- Backfill script: pull 1h and 1d candles from 2021-01-01 (5+ years, covering the Phase 1 training window) for BTCUSDT and ETHUSDT from Binance public klines endpoint (`GET /api/v3/klines`, paginated, 1000 candles/request, no API key required)
- GitHub Actions workflow: cron every hour, pulls latest candles, upserts into `candles` (idempotent — safe to re-run)
- Simple verification script: counts rows per symbol/timeframe, reports gaps

**Exit condition:** Data lands hourly without manual intervention; backfill complete with no gaps.

## Phase 0.5 — Monitor Page (minimal dashboard)

**Goal:** A live, deployed page proving the pipeline is running. Small scope — one session of work.

**Deliverables:**
- New Next.js app in `dashboard/` (App Router, TypeScript, Tailwind), deployed to Vercel as its own project (root directory: `dashboard/`)
- One page with:
  - BTC and ETH candlestick charts (lightweight-charts library) reading from the `candles` table, timeframe toggle (1h/1d)
  - Data-health strip: latest candle timestamp per symbol/timeframe, total row counts, and a freshness indicator (green if latest 1h candle < 2 hours old, red otherwise)
- Supabase access from the dashboard uses the **anon key only**, with Row Level Security enabled and a read-only policy on `candles`. The service role key never appears in dashboard code or Vercel env vars.
- Design extensibility note: in Phase 1 this page gains backtest entry/exit markers overlaid on the chart; in Phase 2 it gains live signal markers and an equity curve. Structure components accordingly, but do NOT build those features now.

**Exit condition:** Owner can open a public URL (or auth-gated page) on their phone and see fresh candles with a green freshness indicator.

## Phase 1 — Backtesting Lab (local, WSL2)

**Goal:** Owner can test strategy ideas against history and judge whether results are trustworthy.

**Deliverables:**
- Python environment with `backtesting.py` (preferred for readability) reading candles from Supabase
- Two reference strategies implemented:
  - `ma_cross_v1`: moving-average crossover (trend-following), e.g. 20/50 on 1d
  - `rsi_revert_v1`: RSI mean-reversion, e.g. RSI(14) < 30 buy / > 70 exit
- Train/validation split: tune on 2021–2023, validate on 2024–2026
- Standard report per backtest: expectancy, win rate, max drawdown, trade count, equity curve, fee-adjusted
- Comparison doc: which strategy survives out-of-sample and why

**Exit condition:** Owner can read a backtest report and articulate whether the result is trustworthy or overfit.

## Phase 2 — Signal Engine (manual/paper mode)

**Goal:** Daily signals with full reasoning, delivered to phone, acted on manually with paper money.

**Deliverables:**
- Daily GitHub Actions job: runs the validated strategy on fresh candles, writes to `signals` table
- Each signal includes: direction, entry, stop-loss, take-profit, position size (risk-based), ELI5 reasoning, and historical stats for the setup
- Telegram bot: pushes new signals and a daily "no trade today" heartbeat
- Dashboard: extend the Phase 0.5 monitor page — signal markers (entry/stop/target) on the candle chart, signals table with reasoning, equity curve from paper trades
- Paper trade logging flow: owner records entries/exits in `trades` table (simple form on dashboard or via Telegram commands)

**Exit condition:** 20–30 paper trades logged with outcomes.

## Phase 3 — Review Ritual (ongoing)

**Goal:** Systematic weekly review; strategy changes are evidence-driven, not reactive.

**Deliverables:**
- Weekly summary script: pulls the week's signals + outcomes, compares actuals vs backtest expectations, outputs a markdown report (Telegram + saved to repo)
- Review template for Obsidian: what diverged, why, hypothesis, decision
- Rules enforced in process:
  - No strategy parameter changes more than once per month
  - No changes based on fewer than 30 trades of evidence
  - Every change logged in `strategies` registry as a new version (never mutate, always version: `ma_cross_v1` → `ma_cross_v2`)

**Exit condition (gate to Phase 4):** 3–6 months of paper trading with positive expectancy after fees, through at least one drawdown period.

## Phase 4 — Automation (small, gated)

**Goal:** Remove the human from execution, with hard safety limits. Nothing about strategy changes.

**Deliverables:**
- Dedicated hot wallet funded only with risk capital (start ~RM50–100 equivalent per position)
- Execution module: translates signals into on-chain orders (SushiSwap spot on Katana, or Katana perps via existing MCP tooling)
- Hard-coded safety limits (in code, not config):
  - Max position size cap
  - Max concurrent positions: 1–2
  - Kill switch: if drawdown from peak exceeds threshold (e.g. 15%), disable the execution cron and alert
- Daily Telegram report: positions, PnL, equity
- Dry-run mode: full pipeline runs but logs intended orders instead of sending, for 2 weeks before going live

**Exit condition:** One month of live trading at minimum size with no execution errors before any scaling discussion.

## Conventions for Claude Code

- Python for data/backtest/signal code; TypeScript only in `dashboard/`
- All secrets via GitHub Actions secrets / Vercel env vars — never committed. Service role key lives ONLY in GitHub Actions; the dashboard uses the anon key with RLS
  - *Phase 2 amendment (2026-06-12, approved in PHASE_2_PROMPT):* the service role key additionally lives in a **server-side** Vercel env var, used exclusively by Next.js API routes (the PIN-gated `/api/log` write path for manual fill logging) — never in `NEXT_PUBLIC_` vars or browser bundles (verified by grep at build time)
- This project never touches or references the Tiger Foundation Dashboard or its repo/Supabase/Vercel resources
- All cron jobs idempotent and safe to re-run
- Each phase is a separate milestone; do not build ahead of the current phase
- When evaluating any strategy or result, report expectancy, max drawdown, and sample size — flag any conclusion drawn from <30 trades as statistically weak
- Strategy code lives in `strategies/` with one file per version; versions are immutable once a strategy enters paper mode

## What Success Looks Like

Phase 1–3 are the product. A conclusion of "no exploitable edge after fees at this capital size" reached through clean methodology is a successful outcome. Phase 4 only ever executes what Phases 1–3 have already proven.
