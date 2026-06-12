# donchian_v1 - ETHUSDT - train window

Window: 2021-01-01 -> 2023-12-31  |  Generated: 2026-06-12 05:54 UTC

## Headline

- **Expectancy per trade (after fees): 1.37%** **[STATISTICALLY WEAK: 15 trades < 30]**
- Trades: 15 (below 30 - every metric here is weak evidence)
- Win rate: 26.67%  |  Avg win: 14.35%  |  Avg loss: -3.35%

## Risk and return

- Strategy total return: 3.23%  |  CAGR: 1.07%
- Max drawdown: -12.39%
- Time in market: 17.72%

## vs Buy & Hold (same window)

- HODL total return: 210.15%  |  CAGR: 45.92%  |  Max drawdown: -81.12%
- Strategy return 3.23% vs HODL 210.15%; strategy drawdown -12.39% vs HODL -81.12%

## Parameters

- Fees: 0.0020 per side (fee + slippage), applied on entry and exit
- entry_days: 20
- exit_days: 10
- regime_days: 200
- atr_mult: 2.0
- atr_n: 14
- risk_pct: 0.01

_Entries fill at the next candle's open; signals use closed candles only (no lookahead). Stops anchored to the signal close. Sizing: stop-out loses 1% of equity, capped at 99% (spot, no leverage). Whole-unit sizing is negligible at cash=1e8. The window's first regime_n bars are indicator warmup._
