# donchian_v1 - ETHUSDT - validation window

Window: 2024-01-01 -> 2026-06-12  |  Generated: 2026-06-12 05:54 UTC

## Headline

- **Expectancy per trade (after fees): 3.95%** **[STATISTICALLY WEAK: 7 trades < 30]**
- Trades: 7 (below 30 - every metric here is weak evidence)
- Win rate: 42.86%  |  Avg win: 15.16%  |  Avg loss: -4.47%

## Risk and return

- Strategy total return: 9.63%  |  CAGR: 3.83%
- Max drawdown: -6.63%
- Time in market: 9.09%

## vs Buy & Hold (same window)

- HODL total return: -26.67%  |  CAGR: -11.92%  |  Max drawdown: -67.83%
- Strategy return 9.63% vs HODL -26.67%; strategy drawdown -6.63% vs HODL -67.83%

## Parameters

- Fees: 0.0020 per side (fee + slippage), applied on entry and exit
- entry_days: 20
- exit_days: 10
- regime_days: 200
- atr_mult: 2.0
- atr_n: 14
- risk_pct: 0.01

_Entries fill at the next candle's open; signals use closed candles only (no lookahead). Stops anchored to the signal close. Sizing: stop-out loses 1% of equity, capped at 99% (spot, no leverage). Whole-unit sizing is negligible at cash=1e8. The window's first regime_n bars are indicator warmup._
