# ma_cross_v1 - ETHUSDT - train window

Window: 2021-01-01 -> 2023-12-31  |  Generated: 2026-06-12 00:23 UTC

## Headline

- **Expectancy per trade (after fees): 6.73%** **[STATISTICALLY WEAK: 2 trades < 30]**
- Trades: 2 (below 30 - every metric here is weak evidence)
- Win rate: 100.00%  |  Avg win: 6.73%  |  Avg loss: n/a

## Risk and return

- Strategy total return: 1.16%  |  CAGR: 0.39%
- Max drawdown: -3.68%
- Time in market: 9.68%

## vs Buy & Hold (same window)

- HODL total return: 209.86%  |  CAGR: 45.88%  |  Max drawdown: -79.30%
- Strategy return 1.16% vs HODL 209.86%; strategy drawdown -3.68% vs HODL -79.30%

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
