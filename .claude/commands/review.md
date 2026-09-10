Run scripts/weekly_review.py, then read the output and the last three entries in reviews/.

Summarize what diverged from the Phase 1d expectations (ETH +1.63%/trade, BTC -0.09%/trade, ~5.8 trades/month combined), flag any unlogged ETH signals prominently, and state the Phase 4 gate status as "N of 7 conditions met" per GO_LIVE_BENCHMARK.md.

Do not propose strategy changes unless scripts/propose_revision.py's gates would pass. If asked to change anything, run it with --status and state which gate blocks.

Report streaks and expectancy factually, always alongside their expected percentile band. A losing streak is not evidence against the strategy: ~22 of every 30 trades are expected to lose.
