# ma_cross_v1_4h - BTCUSDT - train window

Window: 2021-01-01 -> 2023-12-31  |  Generated: 2026-06-12 05:37 UTC

## Headline

- **Expectancy per trade (after fees): -0.35%** **[STATISTICALLY WEAK: 13 trades < 30]**
- Trades: 13 (below 30 - every metric here is weak evidence)
- Win rate: 15.38%  |  Avg win: 15.37%  |  Avg loss: -3.20%

## Risk and return

- Strategy total return: -5.57%  |  CAGR: -1.90%
- Max drawdown: -10.90%
- Time in market: 5.24%

## vs Buy & Hold (same window)

- HODL total return: 45.82%  |  CAGR: 13.42%  |  Max drawdown: -77.04%
- Strategy return -5.57% vs HODL 45.82%; strategy drawdown -10.90% vs HODL -77.04%

## Parameters

- Fees: 0.0020 per side (fee + slippage), applied on entry and exit
- fast_n: 20
- slow_n: 50
- regime_n: 1200
- atr_mult: 2.0
- vol_n: 20
- atr_n: 14
- risk_pct: 0.01

_Entries fill at the next candle's open; signals use closed candles only (no lookahead). Stops anchored to the signal close. Sizing: stop-out loses 1% of equity, capped at 99% (spot, no leverage). Whole-unit sizing is negligible at cash=1e8. The window's first regime_n bars are indicator warmup._
