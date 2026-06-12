# donchian_v1 - BTCUSDT - train window

Window: 2021-01-01 -> 2023-12-31  |  Generated: 2026-06-12 05:54 UTC

## Headline

- **Expectancy per trade (after fees): 3.52%** **[STATISTICALLY WEAK: 13 trades < 30]**
- Trades: 13 (below 30 - every metric here is weak evidence)
- Win rate: 38.46%  |  Avg win: 15.06%  |  Avg loss: -3.69%

## Risk and return

- Strategy total return: 18.86%  |  CAGR: 5.94%
- Max drawdown: -5.53%
- Time in market: 18.16%

## vs Buy & Hold (same window)

- HODL total return: 45.82%  |  CAGR: 13.42%  |  Max drawdown: -77.04%
- Strategy return 18.86% vs HODL 45.82%; strategy drawdown -5.53% vs HODL -77.04%

## Parameters

- Fees: 0.0020 per side (fee + slippage), applied on entry and exit
- entry_days: 20
- exit_days: 10
- regime_days: 200
- atr_mult: 2.0
- atr_n: 14
- risk_pct: 0.01

_Entries fill at the next candle's open; signals use closed candles only (no lookahead). Stops anchored to the signal close. Sizing: stop-out loses 1% of equity, capped at 99% (spot, no leverage). Whole-unit sizing is negligible at cash=1e8. The window's first regime_n bars are indicator warmup._
