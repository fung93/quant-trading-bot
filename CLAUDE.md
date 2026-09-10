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
  Account: $230 paper, 1% risk, 10% kill switch, 95% position cap,
  measured fees 0.10%/side. Evidence basis: PHASE1D_VERDICT.md (ETH
  validation +1.63%/trade on 80 trades — the lab's first validated cell);
  EXPERIMENT_LEDGER.md tracks all families. strategies/tsmom_v1.py is now
  IMMUTABLE (paper mode).
  **Real-capital gate is pre-registered and FROZEN in
  backtest/reports/GO_LIVE_BENCHMARK.md** (≥30 ETH trades, ≥+0.5%/trade
  after fees, survived a drawdown, beat HODL risk-adjusted, legal/tax
  preconditions). Do not move to real money, or weaken that bar, outside its
  Amendment rule.
- Do not build beyond the current phase.
- This project is fully separate from all of the owner's other projects —
  never reference, import from, or modify their repos, Supabase projects, or
  Vercel deployments.
