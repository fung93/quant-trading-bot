# Robustness grid - donchian_v1 - TRAINING window only

Window: 2021-01-01 -> 2023-12-31  |  Generated: 2026-06-12 05:55 UTC

Read this for *stability*, not for a winner. If only one combination
shows positive expectancy, that is an overfitting warning. No
combination is auto-selected.

## BTCUSDT

| entry/exit | ATR x | trades | expectancy/trade | total return | max DD |
|-----------|-------|--------|------------------|--------------|--------|
| 10d/5d | 1.5 | 19 (<30: weak) | +2.78% | +20.59% | -7.61% |
| 10d/5d | 2.0 | 19 (<30: weak) | +2.40% | +12.99% | -6.53% |
| 10d/5d | 3.0 | 19 (<30: weak) | +1.68% | +5.56% | -5.40% |
| 20d/10d | 1.5 | 13 (<30: weak) | +3.91% | +27.10% | -6.63% |
| 20d/10d | 2.0 | 13 (<30: weak) | +3.52% | +18.86% | -5.53% |
| 20d/10d | 3.0 | 11 (<30: weak) | +4.78% | +13.17% | -3.90% |
| 55d/28d | 1.5 | 10 (<30: weak) | +2.03% | +14.59% | -11.49% |
| 55d/28d | 2.0 | 10 (<30: weak) | +1.52% | +9.71% | -9.30% |
| 55d/28d | 3.0 | 8 (<30: weak) | +3.17% | +8.07% | -5.30% |

Positive-expectancy cells: 9/9.

## ETHUSDT

| entry/exit | ATR x | trades | expectancy/trade | total return | max DD |
|-----------|-------|--------|------------------|--------------|--------|
| 10d/5d | 1.5 | 23 (<30: weak) | +2.92% | +9.57% | -11.97% |
| 10d/5d | 2.0 | 21 (<30: weak) | +3.07% | +6.91% | -8.94% |
| 10d/5d | 3.0 | 20 (<30: weak) | +2.94% | +2.95% | -8.19% |
| 20d/10d | 1.5 | 16 (<30: weak) | +1.49% | +5.27% | -14.76% |
| 20d/10d | 2.0 | 15 (<30: weak) | +1.37% | +3.23% | -12.39% |
| 20d/10d | 3.0 | 14 (<30: weak) | +1.48% | +1.66% | -9.01% |
| 55d/28d | 1.5 | 16 (<30: weak) | -1.38% | -4.70% | -19.48% |
| 55d/28d | 2.0 | 14 (<30: weak) | -1.85% | -3.84% | -16.16% |
| 55d/28d | 3.0 | 11 (<30: weak) | -1.66% | -1.31% | -10.01% |

Positive-expectancy cells: 6/9.

## How to read this

- Stable edge: most cells positive, similar magnitudes -> parameters
  are not doing the heavy lifting.
- One hot cell amid noise: overfitting warning - the 'edge' is the
  parameter choice, not the market behavior.
- All trade counts here are far below 30: every number on this page
  is statistically weak evidence either way.
