# Decision log

Working notes kept by Claude across sessions while building this bot, copied
here so the *reasoning* behind decisions survives outside one machine. Commit
messages record what changed; these record why, and what was wrong before.

Names and local paths are replaced with "the owner" and placeholders. The
figures are the same ones already published in `reviews/`.

Read these as a historical log, not as current truth: each entry reflects what
was believed when it was written, and several were later corrected. Where a
note contradicts the code, the code wins.

# Memory index

- [Guide step by step](guide-step-by-step.md) — the owner wants everything guided one step at a time, waiting for his confirmation before the next
- [quant-bot Phase 0 state](quant-bot-phase-0-state.md) — Phase 3 live: 2/30 ETH trades closed (+7.06%, +32.10%); ETH fills stay MANUAL (auto-fill built then reverted 2026-10-09); cron PAT renewed to 2027-10-09; /log no longer pre-fills price (slippage was measuring nothing); criterion 7 rescored on its real text -> **0 of 7** gates met, never 1
- [Binance API blocked in Malaysia](binance-api-blocked-malaysia.md) — use data-api.binance.vision locally; api.binance.com times out
