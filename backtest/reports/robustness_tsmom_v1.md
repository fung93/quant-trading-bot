# Robustness grid - tsmom_v1 - TRAINING window only

Window: 2021-01-01 -> 2023-12-31  |  Generated: 2026-06-12 10:22 UTC

Read this for *stability*, not for a winner. If only one combination
shows positive expectancy, that is an overfitting warning. No
combination is auto-selected.

## BTCUSDT

| lookback | ATR x | trades | expectancy/trade | total return | max DD |
|-----------|-------|--------|------------------|--------------|--------|
| 14d | 1.5 | 170 | +0.33% | +50.89% | -22.25% |
| 14d | 2.0 | 170 | +0.25% | +38.95% | -18.24% |
| 14d | 3.0 | 170 | +0.22% | +24.33% | -13.20% |
| 30d | 1.5 | 82 | +1.49% | +65.51% | -10.87% |
| 30d | 2.0 | 82 | +1.40% | +50.72% | -9.28% |
| 30d | 3.0 | 82 | +2.04% | +62.84% | -7.77% |
| 90d | 1.5 | 62 | +0.14% | +7.21% | -18.01% |
| 90d | 2.0 | 62 | +0.01% | +2.47% | -16.11% |
| 90d | 3.0 | 62 | -0.15% | -0.70% | -12.53% |

Positive-expectancy cells: 8/9.

## ETHUSDT

| lookback | ATR x | trades | expectancy/trade | total return | max DD |
|-----------|-------|--------|------------------|--------------|--------|
| 14d | 1.5 | 149 | +0.56% | +26.24% | -23.42% |
| 14d | 2.0 | 149 | +0.63% | +21.52% | -19.62% |
| 14d | 3.0 | 149 | +0.63% | +11.82% | -15.35% |
| 30d | 1.5 | 102 | +1.51% | +60.41% | -21.85% |
| 30d | 2.0 | 102 | +1.46% | +41.37% | -17.68% |
| 30d | 3.0 | 102 | +1.58% | +27.76% | -12.80% |
| 90d | 1.5 | 40 | -0.29% | +4.85% | -16.05% |
| 90d | 2.0 | 40 | -0.54% | +0.69% | -13.85% |
| 90d | 3.0 | 40 | -0.95% | -2.22% | -11.01% |

Positive-expectancy cells: 6/9.

## How to read this

- Stable edge: most cells positive, similar magnitudes -> parameters
  are not doing the heavy lifting.
- One hot cell amid noise: overfitting warning - the 'edge' is the
  parameter choice, not the market behavior.
- All trade counts here are far below 30: every number on this page
  is statistically weak evidence either way.
