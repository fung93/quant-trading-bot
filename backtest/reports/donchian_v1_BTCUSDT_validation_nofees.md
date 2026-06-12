# donchian_v1 - BTCUSDT - validation window

Window: 2024-01-01 -> 2026-06-12  |  Generated: 2026-06-12 05:55 UTC

> **WARNING: fees disabled - verification run only, not evidence.**

## Headline

- **Expectancy per trade (after fees): 0.28%** **[STATISTICALLY WEAK: 19 trades < 30]**
- Trades: 19 (below 30 - every metric here is weak evidence)
- Win rate: 15.79%  |  Avg win: 13.36%  |  Avg loss: -2.18%

## Risk and return

- Strategy total return: -1.36%  |  CAGR: -0.56%
- Max drawdown: -9.37%
- Time in market: 16.33%

## vs Buy & Hold (same window)

- HODL total return: 50.24%  |  CAGR: 18.11%  |  Max drawdown: -51.92%
- Strategy return -1.36% vs HODL 50.24%; strategy drawdown -9.37% vs HODL -51.92%

## Parameters

- Fees: 0.0000 per side (fee + slippage), applied on entry and exit
- entry_days: 20
- exit_days: 10
- regime_days: 200
- atr_mult: 2.0
- atr_n: 14
- risk_pct: 0.01

_Entries fill at the next candle's open; signals use closed candles only (no lookahead). Stops anchored to the signal close. Sizing: stop-out loses 1% of equity, capped at 99% (spot, no leverage). Whole-unit sizing is negligible at cash=1e8. The window's first regime_n bars are indicator warmup._
