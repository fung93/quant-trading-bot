# Robustness grid - ma_cross_v1 - TRAINING window only

Window: 2021-01-01 -> 2023-12-31  |  Generated: 2026-06-12 00:25 UTC

Read this for *stability*, not for a winner. If only one combination
shows positive expectancy, that is an overfitting warning. No
combination is auto-selected.

## BTCUSDT

| fast/slow | ATR x | trades | expectancy/trade | total return | max DD |
|-----------|-------|--------|------------------|--------------|--------|
| 10/50 | 1.5 | 2 (<30: weak) | +0.44% | -0.23% | -3.41% |
| 10/50 | 2.0 | 2 (<30: weak) | +0.72% | -0.09% | -2.51% |
| 10/50 | 3.0 | 2 (<30: weak) | +0.72% | -0.06% | -1.68% |
| 20/50 | 1.5 | 1 (<30: weak) | -5.18% | -0.73% | -3.31% |
| 20/50 | 2.0 | 1 (<30: weak) | -5.18% | -0.55% | -2.49% |
| 20/50 | 3.0 | 1 (<30: weak) | -5.18% | -0.37% | -1.68% |
| 20/100 | 1.5 | 3 (<30: weak) | +10.93% | +8.28% | -5.20% |
| 20/100 | 2.0 | 3 (<30: weak) | +10.48% | +5.98% | -4.18% |
| 20/100 | 3.0 | 3 (<30: weak) | +21.85% | +8.47% | -2.71% |
| 50/200 | 1.5 | 1 (<30: weak) | -5.06% | -1.08% | -1.08% |
| 50/200 | 2.0 | 1 (<30: weak) | -6.61% | -1.06% | -1.06% |
| 50/200 | 3.0 | 1 (<30: weak) | -9.71% | -1.04% | -1.74% |

Positive-expectancy cells: 6/12.

## ETHUSDT

| fast/slow | ATR x | trades | expectancy/trade | total return | max DD |
|-----------|-------|--------|------------------|--------------|--------|
| 10/50 | 1.5 | 4 (<30: weak) | -0.96% | -0.36% | -2.56% |
| 10/50 | 2.0 | 4 (<30: weak) | -0.96% | -0.27% | -1.93% |
| 10/50 | 3.0 | 4 (<30: weak) | -0.96% | -0.18% | -1.30% |
| 20/50 | 1.5 | 2 (<30: weak) | +6.73% | +1.55% | -4.85% |
| 20/50 | 2.0 | 2 (<30: weak) | +6.73% | +1.16% | -3.68% |
| 20/50 | 3.0 | 2 (<30: weak) | +6.73% | +0.77% | -2.49% |
| 20/100 | 1.5 | 4 (<30: weak) | +2.23% | +2.76% | -5.08% |
| 20/100 | 2.0 | 4 (<30: weak) | +1.02% | +1.58% | -4.32% |
| 20/100 | 3.0 | 4 (<30: weak) | +8.53% | +2.50% | -2.90% |
| 50/200 | 1.5 | 3 (<30: weak) | +0.19% | +0.76% | -5.10% |
| 50/200 | 2.0 | 3 (<30: weak) | +4.71% | +1.56% | -4.95% |
| 50/200 | 3.0 | 3 (<30: weak) | +10.77% | +2.35% | -3.22% |

Positive-expectancy cells: 9/12.

## How to read this

- Stable edge: most cells positive, similar magnitudes -> parameters
  are not doing the heavy lifting.
- One hot cell amid noise: overfitting warning - the 'edge' is the
  parameter choice, not the market behavior.
- All trade counts here are far below 30: every number on this page
  is statistically weak evidence either way.
