"""ma_cross_v1 — trend-following MA crossover (Phase 1 reference strategy).

Long-only. Gate structure, evaluated at each daily close:
  Gate 1 (regime):  Close > SMA(200); if false, no entries and any open
                    position is closed.
  Gate 2 (trigger): SMA(fast) crosses above SMA(slow) at this candle.
  Gate 3 (volume):  Volume > SMA(Volume, 20).
Entry at next open (backtesting.py default — no trade_on_close, no
lookahead). Stop: signal close − atr_mult × ATR(14), held as a hard stop.
Exit: stop hit, SMA(fast) crosses back below SMA(slow), or regime fails.
Sizing: risk-based — a stop-out loses risk_pct of current equity, capped at
99% of equity (spot, no leverage).

Strategy versions are immutable once they enter paper mode (BUILD_PLAN).
"""

import math

from backtesting import Strategy
from backtesting.lib import crossover

from backtest.config import RISK_PCT
from backtest.indicators import atr, sma


class MaCrossV1(Strategy):
    # Parameters exposed for optimization (training window only).
    fast_n = 20
    slow_n = 50
    regime_n = 200
    atr_mult = 2.0
    vol_n = 20
    atr_n = 14
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
        # Fraction of equity such that (entry - stop) loses risk_pct.
        frac = min(self.risk_pct * price / (price - stop), 0.99)
        self.buy(size=frac, sl=stop)
