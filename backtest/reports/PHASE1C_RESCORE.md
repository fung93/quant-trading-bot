# Phase 1c re-score - donchian_v1 under the measured fee model

Generated: 2026-06-12 10:19 UTC. Parameters byte-identical to 1c (a-priori Turtle
defaults: entry 20d, exit 10d, ATR x2.0, regime 200d - frozen since
before any 1c run; see PHASE1C_VERDICT.md provenance). Old model:
0.20%/side (0.4% RT, a-priori). New model: 0.10%/side (0.20% RT,
measured on Sushi/Katana - see EXPERIMENT_LEDGER.md).

| Symbol | Window | Trades | Expectancy (old -> new) | Total return (old -> new) | Max DD (old -> new) |
|---|---|---|---|---|---|
| BTCUSDT | train | 13 (<30: weak) | +3.52% -> **+3.72%** | +18.86% -> +19.83% | -5.53% -> -5.39% |
| BTCUSDT | validation | 19 (<30: weak) | -0.12% -> **+0.08%** | -4.71% -> -3.05% | -10.73% -> -10.06% |
| ETHUSDT | train | 15 (<30: weak) | +1.37% -> **+1.57%** | +3.23% -> +4.22% | -12.39% -> -11.83% |
| ETHUSDT | validation | 7 (<30: weak) | +3.95% -> **+4.15%** | +9.63% -> +10.06% | -6.63% -> -6.52% |

Trade sequences identical under both fee models: **True** (entry/exit bars compared trade-by-trade; signals are equity-independent, so only the per-trade cost arithmetic changed).

## What changed, and what did not

- **BTC validation expectancy moved from -0.12% to +0.08% per trade** - the sign flip the 1c verdict predicted would hinge on the fee line. This is arithmetic on the same 19 trades, not new evidence of skill.
- Every other cell shifts by the same per-trade fee delta; no ranking between cells changes.
- **Classification is unchanged: weak/uncertain.** All samples remain far below 30 trades; a result whose sign depends on the fee model within one round-trip's width is, by definition, thin. The measured model makes the arithmetic honest - it does not make the evidence strong.
