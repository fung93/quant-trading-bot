# Experiment Ledger — every mechanism family tested through this lab

**Purpose: multiple-comparisons honesty.** Each additional family tested
raises the odds that one of them looks good by chance, so the more rows
this table grows, the more skeptically any single "pass" must be read. A
strategy that tests well after 10 tries is weaker evidence than the same
result on try 1. Every future verdict adds or updates a row here.

| # | Family / version | Timeframe | Verdict | Doc |
|---|------------------|-----------|---------|-----|
| 1 | MA-cross + volume gate (ma_cross_v1) | 1d | Rejected — sample starvation (6 trades / 5.5y across all runs) | PHASE1_VERDICT.md |
| 2 | MA-cross + volume gate (ma_cross_v1_4h) | 4h | Rejected — family-level: negative training both assets, ETH 0/12 grid cells positive | PHASE1B_VERDICT.md |
| 3 | Donchian breakout (donchian_v1) | 4h | **Weak/uncertain** — first family to pass its training window on both assets (grid: BTC 9/9, ETH 6/9 positive, assets agree at 10–20d); validation mixed (ETH +3.95%/7 trades, BTC −0.12%/19 — positive before fees, negative after); all samples <30. Re-scored under measured fees (PHASE1C_RESCORE.md): all four cells positive, BTC validation +0.08%; classification unchanged | PHASE1C_VERDICT.md |
| 4 | Time-series momentum (tsmom_v1) | 4h | **Weak-positive** — first real samples (80–102 trades/cell, no weak flags); training +1.40%/+1.46% both assets; validation ETH **+1.63%/80 trades = first cell meeting every pre-registered validation criterion**; BTC validation flat (−0.09%/90); grid: assets agree in shape, 30d sweet spot on both, 90d dead on both | PHASE1D_VERDICT.md |

## Fee model revision (2026-06-12)

Phases 1/1b/1c ran on the a-priori assumption of 0.2% per side (0.4%
round trip). After the execution venue was decided (Sushi spot on Katana),
the real cost was measured via live round-trip quotes at $1,000 size on
2026-06-12: USDC↔WETH **0.152%** RT, USDC↔WBTC **0.146%** RT, through V3
0.05% fee-tier pools; gas negligible. Adopted: **0.10% per side (0.20%
RT)** — measured ~0.15% plus a safety margin for liquidity thinning.

This is a measurement-driven change made after venue selection — **with a
pre-commitment that a worse measurement would equally have been adopted.**
The 1c results were re-SCORED (identical parameters, same data, new cost
arithmetic only — no re-tuning): see PHASE1C_RESCORE.md. Historical
verdicts (PHASE1*, robustness tables) retain the old fee model and are
not retroactively edited.

## Pre-registered stopping rule

If Donchian (#3) and time-series momentum (the planned #4, if needed)
**both fail on both assets**, the conclusion is: *trend-following on
BTC/ETH at 4h/1d does not survive our fee model* — and the next hypothesis
must come from a different signal source entirely (not another trend
variant).

Status after #3: **rule not triggered** — Donchian did not fail on both
assets (positive training expectancy on both; stable grid region where the
assets agree). It also did not validate. See PHASE1C_VERDICT.md for what
evidence would move it either way.

Status after #4 (final): **rule decisively not triggered.** Both trend
families passed training on both assets; TSMOM produced the lab's first
fully validated cell (ETH validation, +1.63%/trade on 80 trades after
measured fees). Conclusion: trend-following on BTC/ETH at 4h *survives*
the measured fee model — thin, asset- and regime-dependent (BTC 2024–2026
flat for both mechanisms), strongest as TSMOM-30d on ETH. The convergence
of two independent mechanisms on the same structural story is the
strongest evidence this lab has produced. See PHASE1D_VERDICT.md.
