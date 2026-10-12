# CLAUDE.md

Read BUILD_PLAN.md before any work.

- **Current phase: 3 (paper trading + weekly review). Strategy: tsmom_v1.
  Strategy changes only via the Phase 3 revision rules.**
  Weekly review: scripts/weekly_review.py (Sun 09:00 MYT, weekly-review.yml),
  output to reviews/. Revisions ONLY via scripts/propose_revision.py, which
  refuses anything under 30 closed trades, under 30 days since the last
  revision, any mutation of an existing version, or a thin justification.
  Gate tracker (7 frozen criteria) in the review and on /signals.
  ETH primary (owner logs fills at /log), BTC observational (auto-filled,
  excluded from equity/kill switch). Engine: scripts/signal_engine.py,
  every 4h via signal-engine.yml (sync runs first in the same job).
  **Position size is recomputed at log time** from the price actually
  filled, never inherited from the signal (/api/log). The rule is "risk 1%
  of equity"; units are derived from it. A late fill at a worse price with
  an unchanged stop silently breaks that rule - 2026-10-10, 1.48% risk on
  a signal delivered 18.7h late. A failing engine run now also alerts on
  Telegram: six silent red runs preceded that incident.
  **BOTH symbols auto-fill at next bar open** (auto_fill in signal_engine).
  That is the price the strategy could actually transact at and what
  backtesting.py assumes. ETH was manual until 2026-10-12, when the owner
  moved execution to the engine; his late logging had been corrupting the
  sample (two crosses dropped in Aug, a 1.33% worse entry in Oct, ~24h mean
  lateness on 4h bars). ETH fills are marked status 'autofilled' so the
  record shows what executed them - information, not a penalty.
  **Size is always recomputed at the fill price** (size_for_fill, and
  /api/log for manual logs): never inherit the signal's unit count, which
  was derived from the signal-bar price. warn_primary_unfilled alarms if an
  ETH signal stays pending >4h, which now means a fill FAILED.
  Criterion 7 is scored on its frozen text only - "a faithful price near
  signal time" - which names no executor. An owner-execution requirement
  (mine, 2026-10-09..10-12) was removed: the benchmark says plainly that
  paper cannot test the owner, and routes that to the mandated Phase 4
  2-week dry run. Pending signals and fills beyond 4h still fail it.
  **Real-capital gate is pre-registered and FROZEN in
  backtest/reports/GO_LIVE_BENCHMARK.md** (≥30 ETH trades, ≥+0.5%/trade
  after fees, survived a drawdown, beat HODL risk-adjusted, legal/tax
  preconditions). Do not move to real money, or weaken that bar, outside its
  Amendment rule.
- Do not build beyond the current phase.
- This project is fully separate from all of the owner's other projects —
  never reference, import from, or modify their repos, Supabase projects, or
  Vercel deployments.
