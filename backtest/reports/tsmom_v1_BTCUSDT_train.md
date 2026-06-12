# tsmom_v1 - BTCUSDT - train window

Window: 2021-01-01 -> 2023-12-31  |  Generated: 2026-06-12 10:21 UTC

## Headline

- **Expectancy per trade (after fees): 1.40%**
- Trades: 82
- Win rate: 35.37%  |  Avg win: 6.78%  |  Avg loss: -1.54%

## Risk and return

- Strategy total return: 50.72%  |  CAGR: 14.68%
- Max drawdown: -9.28%
- Time in market: 38.67%

## vs Buy & Hold (same window)

- HODL total return: 45.82%  |  CAGR: 13.42%  |  Max drawdown: -77.04%
- Strategy return 50.72% vs HODL 45.82%; strategy drawdown -9.28% vs HODL -77.04%

## Parameters

- Fees: 0.0010 per side (fee + slippage), applied on entry and exit
- lookback_days: 30
- atr_mult: 2.0
- atr_n: 14
- risk_pct: 0.01

_Entries fill at the next candle's open; signals use closed candles only (no lookahead). Stops anchored to the signal close. Sizing: stop-out loses 1% of equity, capped at 99% (spot, no leverage). Whole-unit sizing is negligible at cash=1e8. The window's first regime_n bars are indicator warmup._
