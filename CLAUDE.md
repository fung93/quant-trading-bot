# CLAUDE.md

Read BUILD_PLAN.md before any work.

- **Current phase: 2 (paper trading live). Strategy: tsmom_v1. No strategy
  changes permitted outside Phase 3 rules.**
  ETH primary (owner logs fills at /log), BTC observational (auto-filled,
  excluded from equity/kill switch). Engine: scripts/signal_engine.py,
  every 4h via signal-engine.yml (sync runs first in the same job).
  Account: $230 paper, 1% risk, 10% kill switch, 95% position cap,
  measured fees 0.10%/side. Evidence basis: PHASE1D_VERDICT.md (ETH
  validation +1.63%/trade on 80 trades — the lab's first validated cell);
  EXPERIMENT_LEDGER.md tracks all families. strategies/tsmom_v1.py is now
  IMMUTABLE (paper mode).
- Do not build beyond the current phase.
- This project is fully separate from all of the owner's other projects —
  never reference, import from, or modify their repos, Supabase projects, or
  Vercel deployments.
