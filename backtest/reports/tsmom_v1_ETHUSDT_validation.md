# tsmom_v1 - ETHUSDT - validation window

Window: 2024-01-01 -> 2026-06-12  |  Generated: 2026-06-12 10:22 UTC

## Headline

- **Expectancy per trade (after fees): 1.63%**
- Trades: 80
- Win rate: 26.25%  |  Avg win: 11.59%  |  Avg loss: -1.92%

## Risk and return

- Strategy total return: 50.71%  |  CAGR: 18.27%
- Max drawdown: -16.58%
- Time in market: 40.72%

## vs Buy & Hold (same window)

- HODL total return: -26.67%  |  CAGR: -11.92%  |  Max drawdown: -67.83%
- Strategy return 50.71% vs HODL -26.67%; strategy drawdown -16.58% vs HODL -67.83%

## Parameters

- Fees: 0.0010 per side (fee + slippage), applied on entry and exit
- lookback_days: 30
- atr_mult: 2.0
- atr_n: 14
- risk_pct: 0.01

_Entries fill at the next candle's open; signals use closed candles only (no lookahead). Stops anchored to the signal close. Sizing: stop-out loses 1% of equity, capped at 99% (spot, no leverage). Whole-unit sizing is negligible at cash=1e8. The window's first regime_n bars are indicator warmup._
