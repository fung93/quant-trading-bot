# rsi_revert_v1 - BTCUSDT - train window

Window: 2021-01-01 -> 2023-12-31  |  Generated: 2026-06-12 00:24 UTC

## Headline

- **Expectancy per trade (after fees): 17.98%** **[STATISTICALLY WEAK: 1 trades < 30]**
- Trades: 1 (below 30 - every metric here is weak evidence)
- Win rate: 100.00%  |  Avg win: 17.98%  |  Avg loss: n/a

## Risk and return

- Strategy total return: 2.13%  |  CAGR: 0.71%
- Max drawdown: -0.15%
- Time in market: 0.46%

## vs Buy & Hold (same window)

- HODL total return: 46.19%  |  CAGR: 13.52%  |  Max drawdown: -76.63%
- Strategy return 2.13% vs HODL 46.19%; strategy drawdown -0.15% vs HODL -76.63%

## Parameters

- Fees: 0.0020 per side (fee + slippage), applied on entry and exit
- rsi_n: 14
- entry_th: 30
- exit_th: 55
- regime_n: 200
- atr_mult: 2.0
- atr_n: 14
- risk_pct: 0.01

_Entries fill at the next candle's open; signals use closed candles only (no lookahead). Stops anchored to the signal close. Sizing: stop-out loses 1% of equity, capped at 99% (spot, no leverage). Whole-unit sizing is negligible at cash=1e8. First ~200 bars of each window are indicator warmup._
