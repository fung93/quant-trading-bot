# ma_cross_v1_4h - BTCUSDT - validation window

Window: 2024-01-01 -> 2026-06-12  |  Generated: 2026-06-12 05:38 UTC

> **WARNING: fees disabled - verification run only, not evidence.**

## Headline

- **Expectancy per trade (after fees): 3.24%** **[STATISTICALLY WEAK: 11 trades < 30]**
- Trades: 11 (below 30 - every metric here is weak evidence)
- Win rate: 63.64%  |  Avg win: 6.42%  |  Avg loss: -2.31%

## Risk and return

- Strategy total return: 13.54%  |  CAGR: 5.33%
- Max drawdown: -3.11%
- Time in market: 8.42%

## vs Buy & Hold (same window)

- HODL total return: 50.24%  |  CAGR: 18.11%  |  Max drawdown: -51.92%
- Strategy return 13.54% vs HODL 50.24%; strategy drawdown -3.11% vs HODL -51.92%

## Parameters

- Fees: 0.0000 per side (fee + slippage), applied on entry and exit
- fast_n: 20
- slow_n: 50
- regime_n: 1200
- atr_mult: 2.0
- vol_n: 20
- atr_n: 14
- risk_pct: 0.01

_Entries fill at the next candle's open; signals use closed candles only (no lookahead). Stops anchored to the signal close. Sizing: stop-out loses 1% of equity, capped at 99% (spot, no leverage). Whole-unit sizing is negligible at cash=1e8. The window's first regime_n bars are indicator warmup._
