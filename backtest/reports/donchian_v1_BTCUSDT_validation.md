# donchian_v1 - BTCUSDT - validation window

Window: 2024-01-01 -> 2026-06-12  |  Generated: 2026-06-12 05:54 UTC

## Headline

- **Expectancy per trade (after fees): -0.12%** **[STATISTICALLY WEAK: 19 trades < 30]**
- Trades: 19 (below 30 - every metric here is weak evidence)
- Win rate: 15.79%  |  Avg win: 12.93%  |  Avg loss: -2.57%

## Risk and return

- Strategy total return: -4.71%  |  CAGR: -1.95%
- Max drawdown: -10.73%
- Time in market: 16.33%

## vs Buy & Hold (same window)

- HODL total return: 50.24%  |  CAGR: 18.11%  |  Max drawdown: -51.92%
- Strategy return -4.71% vs HODL 50.24%; strategy drawdown -10.73% vs HODL -51.92%

## Parameters

- Fees: 0.0020 per side (fee + slippage), applied on entry and exit
- entry_days: 20
- exit_days: 10
- regime_days: 200
- atr_mult: 2.0
- atr_n: 14
- risk_pct: 0.01

_Entries fill at the next candle's open; signals use closed candles only (no lookahead). Stops anchored to the signal close. Sizing: stop-out loses 1% of equity, capped at 99% (spot, no leverage). Whole-unit sizing is negligible at cash=1e8. The window's first regime_n bars are indicator warmup._
