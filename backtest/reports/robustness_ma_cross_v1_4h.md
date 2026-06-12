# Robustness grid - ma_cross_v1_4h - TRAINING window only

Window: 2021-01-01 -> 2023-12-31  |  Generated: 2026-06-12 05:37 UTC

Read this for *stability*, not for a winner. If only one combination
shows positive expectancy, that is an overfitting warning. No
combination is auto-selected.

## BTCUSDT

| fast/slow | ATR x | trades | expectancy/trade | total return | max DD |
|-----------|-------|--------|------------------|--------------|--------|
| 10/50 | 1.5 | 24 (<30: weak) | +1.33% | +16.54% | -8.69% |
| 10/50 | 2.0 | 24 (<30: weak) | +0.99% | +9.12% | -7.93% |
| 10/50 | 3.0 | 24 (<30: weak) | +0.88% | +5.65% | -5.23% |
| 20/50 | 1.5 | 13 (<30: weak) | +0.25% | -3.96% | -11.60% |
| 20/50 | 2.0 | 13 (<30: weak) | -0.35% | -5.57% | -10.90% |
| 20/50 | 3.0 | 13 (<30: weak) | -0.49% | -4.41% | -8.42% |
| 20/100 | 1.5 | 9 (<30: weak) | +4.31% | +15.29% | -10.15% |
| 20/100 | 2.0 | 9 (<30: weak) | +3.96% | +10.36% | -8.22% |
| 20/100 | 3.0 | 9 (<30: weak) | +3.20% | +5.28% | -6.51% |
| 50/200 | 1.5 | 2 (<30: weak) | +6.18% | +4.65% | -7.87% |
| 50/200 | 2.0 | 2 (<30: weak) | +6.18% | +3.49% | -6.07% |
| 50/200 | 3.0 | 2 (<30: weak) | +6.18% | +2.32% | -4.16% |

Positive-expectancy cells: 10/12.

## ETHUSDT

| fast/slow | ATR x | trades | expectancy/trade | total return | max DD |
|-----------|-------|--------|------------------|--------------|--------|
| 10/50 | 1.5 | 19 (<30: weak) | -2.38% | -14.31% | -20.89% |
| 10/50 | 2.0 | 19 (<30: weak) | -2.06% | -9.24% | -14.14% |
| 10/50 | 3.0 | 19 (<30: weak) | -2.24% | -6.92% | -10.22% |
| 20/50 | 1.5 | 11 (<30: weak) | -3.29% | -11.99% | -11.99% |
| 20/50 | 2.0 | 11 (<30: weak) | -4.19% | -11.51% | -11.51% |
| 20/50 | 3.0 | 11 (<30: weak) | -3.25% | -6.91% | -9.82% |
| 20/100 | 1.5 | 9 (<30: weak) | -2.84% | -8.50% | -15.90% |
| 20/100 | 2.0 | 9 (<30: weak) | -3.47% | -7.87% | -13.58% |
| 20/100 | 3.0 | 9 (<30: weak) | -1.20% | -2.54% | -6.65% |
| 50/200 | 1.5 | 4 (<30: weak) | -2.74% | -4.21% | -4.66% |
| 50/200 | 2.0 | 4 (<30: weak) | -3.38% | -3.90% | -4.41% |
| 50/200 | 3.0 | 4 (<30: weak) | -0.93% | -1.46% | -3.81% |

Positive-expectancy cells: 0/12.

## How to read this

- Stable edge: most cells positive, similar magnitudes -> parameters
  are not doing the heavy lifting.
- One hot cell amid noise: overfitting warning - the 'edge' is the
  parameter choice, not the market behavior.
- All trade counts here are far below 30: every number on this page
  is statistically weak evidence either way.
