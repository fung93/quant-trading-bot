# ma_cross_v1_4h - ETHUSDT - train window

Window: 2021-01-01 -> 2023-12-31  |  Generated: 2026-06-12 05:37 UTC

## Headline

- **Expectancy per trade (after fees): -4.19%** **[STATISTICALLY WEAK: 11 trades < 30]**
- Trades: 11 (below 30 - every metric here is weak evidence)
- Win rate: 0.00%  |  Avg win: n/a  |  Avg loss: -4.19%

## Risk and return

- Strategy total return: -11.51%  |  CAGR: -4.00%
- Max drawdown: -11.51%
- Time in market: 2.13%

## vs Buy & Hold (same window)

- HODL total return: 210.15%  |  CAGR: 45.92%  |  Max drawdown: -81.12%
- Strategy return -11.51% vs HODL 210.15%; strategy drawdown -11.51% vs HODL -81.12%

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
