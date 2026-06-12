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
| 3 | Donchian breakout (donchian_v1) | 4h | **Weak/uncertain** — first family to pass its training window on both assets (grid: BTC 9/9, ETH 6/9 positive, assets agree at 10–20d); validation mixed (ETH +3.95%/7 trades, BTC −0.12%/19 — positive before fees, negative after); all samples <30 | PHASE1C_VERDICT.md |

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
