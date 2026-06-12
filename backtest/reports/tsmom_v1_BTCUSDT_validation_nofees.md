# tsmom_v1 - BTCUSDT - validation window

Window: 2024-01-01 -> 2026-06-12  |  Generated: 2026-06-12 10:24 UTC

> **WARNING: fees disabled - verification run only, not evidence.**

## Headline

- **Expectancy per trade (after fees): 0.11%**
- Trades: 90
- Win rate: 32.22%  |  Avg win: 3.33%  |  Avg loss: -1.42%

## Risk and return

- Strategy total return: 9.07%  |  CAGR: 3.61%
- Max drawdown: -18.54%
- Time in market: 36.54%

## vs Buy & Hold (same window)

- HODL total return: 50.24%  |  CAGR: 18.11%  |  Max drawdown: -51.92%
- Strategy return 9.07% vs HODL 50.24%; strategy drawdown -18.54% vs HODL -51.92%

## Parameters

- Fees: 0.0000 per side (fee + slippage), applied on entry and exit
- lookback_days: 30
- atr_mult: 2.0
- atr_n: 14
- risk_pct: 0.01

_Entries fill at the next candle's open; signals use closed candles only (no lookahead). Stops anchored to the signal close. Sizing: stop-out loses 1% of equity, capped at 99% (spot, no leverage). Whole-unit sizing is negligible at cash=1e8. The window's first regime_n bars are indicator warmup._
