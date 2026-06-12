# ma_cross_v1_4h - ETHUSDT - validation window

Window: 2024-01-01 -> 2026-06-12  |  Generated: 2026-06-12 05:37 UTC

## Headline

- **Expectancy per trade (after fees): 1.54%** **[STATISTICALLY WEAK: 5 trades < 30]**
- Trades: 5 (below 30 - every metric here is weak evidence)
- Win rate: 60.00%  |  Avg win: 5.13%  |  Avg loss: -3.86%

## Risk and return

- Strategy total return: 1.67%  |  CAGR: 0.68%
- Max drawdown: -4.13%
- Time in market: 4.03%

## vs Buy & Hold (same window)

- HODL total return: -26.67%  |  CAGR: -11.92%  |  Max drawdown: -67.83%
- Strategy return 1.67% vs HODL -26.67%; strategy drawdown -4.13% vs HODL -67.83%

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
