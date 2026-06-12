# ma_cross_v1 - BTCUSDT - train window

Window: 2021-01-01 -> 2023-12-31  |  Generated: 2026-06-12 00:23 UTC

## Headline

- **Expectancy per trade (after fees): -5.18%** **[STATISTICALLY WEAK: 1 trades < 30]**
- Trades: 1 (below 30 - every metric here is weak evidence)
- Win rate: 0.00%  |  Avg win: n/a  |  Avg loss: -5.18%

## Risk and return

- Strategy total return: -0.55%  |  CAGR: -0.18%
- Max drawdown: -2.49%
- Time in market: 4.38%

## vs Buy & Hold (same window)

- HODL total return: 46.19%  |  CAGR: 13.52%  |  Max drawdown: -76.63%
- Strategy return -0.55% vs HODL 46.19%; strategy drawdown -2.49% vs HODL -76.63%

## Parameters

- Fees: 0.0020 per side (fee + slippage), applied on entry and exit
- fast_n: 20
- slow_n: 50
- regime_n: 200
- atr_mult: 2.0
- vol_n: 20
- atr_n: 14
- risk_pct: 0.01

_Entries fill at the next candle's open; signals use closed candles only (no lookahead). Stops anchored to the signal close. Sizing: stop-out loses 1% of equity, capped at 99% (spot, no leverage). Whole-unit sizing is negligible at cash=1e8. First ~200 bars of each window are indicator warmup._
