# ma_cross_v1 - BTCUSDT - validation window

Window: 2024-01-01 -> 2026-06-11  |  Generated: 2026-06-12 00:23 UTC

## Headline

- **Expectancy per trade (after fees): -9.05%** **[STATISTICALLY WEAK: 1 trades < 30]**
- Trades: 1 (below 30 - every metric here is weak evidence)
- Win rate: 0.00%  |  Avg win: n/a  |  Avg loss: -9.05%

## Risk and return

- Strategy total return: -1.04%  |  CAGR: -0.43%
- Max drawdown: -1.04%
- Time in market: 1.34%

## vs Buy & Hold (same window)

- HODL total return: 50.47%  |  CAGR: 18.21%  |  Max drawdown: -51.16%
- Strategy return -1.04% vs HODL 50.47%; strategy drawdown -1.04% vs HODL -51.16%

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
