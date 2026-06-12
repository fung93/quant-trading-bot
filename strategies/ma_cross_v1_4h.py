"""ma_cross_v1_4h — ma_cross_v1 re-anchored to 4h decision candles.

Phase 1b experiment: ONE variable changed vs ma_cross_v1 — the decision
timeframe (daily -> 4h). Gate logic is identical.

Anchoring decision (deliberate, per PHASE_1B_PROMPT): the regime filter
stays at the DAILY scale. "Are we in a bull market?" must remain a 200-DAY
question, so Gate 1 uses SMA(1200) of 4h closes (1200 x 4h = 200 days) —
NOT SMA(200) of 4h closes, which would silently turn it into a ~33-day
question. Gates 2-3 (20/50 cross, volume confirmation) and ATR move to 4h
resolution; that finer resolution is the experiment.

ma_cross_v1.py is untouched (immutability convention: new version, new file).
Long-only; entries at next open; stop = signal close − atr_mult × ATR(14);
sizing: a stop-out loses risk_pct of equity, capped at 99% (spot).
"""

import math

from backtesting import Strategy
from backtesting.lib import crossover

from backtest.config import RISK_PCT
from backtest.indicators import atr, sma


class MaCrossV1_4h(Strategy):
    # Parameters exposed for optimization (training window only).
    fast_n = 20        # 4h bars
    slow_n = 50        # 4h bars
    regime_n = 1200    # 4h bars = 200 DAYS (do not shrink; see docstring)
    atr_mult = 2.0
    vol_n = 20         # 4h bars
    atr_n = 14         # 4h bars
    risk_pct = RISK_PCT

    def init(self):
        close = self.data.Close
        self.fast_ma = self.I(sma, close, self.fast_n)
        self.slow_ma = self.I(sma, close, self.slow_n)
        self.regime_ma = self.I(sma, close, self.regime_n)
        self.vol_ma = self.I(sma, self.data.Volume, self.vol_n)
        self.atr_ = self.I(atr, self.data.High, self.data.Low, close, self.atr_n)

    def next(self):
        price = self.data.Close[-1]
        # NaN regime (warmup) compares False -> entries stay blocked.
        regime_ok = price > self.regime_ma[-1]

        if self.position:
            if (not regime_ok) or crossover(self.slow_ma, self.fast_ma):
                self.position.close()
            return

        if not regime_ok:
            return
        if not crossover(self.fast_ma, self.slow_ma):
            return
        if not self.data.Volume[-1] > self.vol_ma[-1]:
            return

        a = self.atr_[-1]
        if math.isnan(a) or a <= 0:
            return
        stop = price - self.atr_mult * a
        if stop <= 0:
            return
        frac = min(self.risk_pct * price / (price - stop), 0.99)
        self.buy(size=frac, sl=stop)
