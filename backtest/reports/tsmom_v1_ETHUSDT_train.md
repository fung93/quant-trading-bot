# tsmom_v1 - ETHUSDT - train window

Window: 2021-01-01 -> 2023-12-31  |  Generated: 2026-06-12 10:22 UTC

## Headline

- **Expectancy per trade (after fees): 1.46%**
- Trades: 102
- Win rate: 36.27%  |  Avg win: 7.42%  |  Avg loss: -1.93%

## Risk and return

- Strategy total return: 41.37%  |  CAGR: 12.25%
- Max drawdown: -17.68%
- Time in market: 42.73%

## vs Buy & Hold (same window)

- HODL total return: 210.15%  |  CAGR: 45.92%  |  Max drawdown: -81.12%
- Strategy return 41.37% vs HODL 210.15%; strategy drawdown -17.68% vs HODL -81.12%

## Parameters

- Fees: 0.0010 per side (fee + slippage), applied on entry and exit
- lookback_days: 30
- atr_mult: 2.0
- atr_n: 14
- risk_pct: 0.01

_Entries fill at the next candle's open; signals use closed candles only (no lookahead). Stops anchored to the signal close. Sizing: stop-out loses 1% of equity, capped at 99% (spot, no leverage). Whole-unit sizing is negligible at cash=1e8. The window's first regime_n bars are indicator warmup._
