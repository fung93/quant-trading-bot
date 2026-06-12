# rsi_revert_v1 - ETHUSDT - train window

Window: 2021-01-01 -> 2023-12-31  |  Generated: 2026-06-12 00:24 UTC

## Headline

- **Expectancy per trade (after fees): n/a** **[STATISTICALLY WEAK: 0 trades < 30]**
- Trades: 0 (below 30 - every metric here is weak evidence)
- Win rate: n/a  |  Avg win: n/a  |  Avg loss: n/a

## Risk and return

- Strategy total return: 0.00%  |  CAGR: 0.00%
- Max drawdown: -0.00%
- Time in market: 0.00%

## vs Buy & Hold (same window)

- HODL total return: 209.86%  |  CAGR: 45.88%  |  Max drawdown: -79.30%
- Strategy return 0.00% vs HODL 209.86%; strategy drawdown -0.00% vs HODL -79.30%

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
