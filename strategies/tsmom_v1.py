"""tsmom_v1 — time-series momentum on 4h candles (ledger family #4).

The simplest trend mechanism in the literature: long while the asset is
above its own price N days ago, flat otherwise.

NO separate 200-day regime gate — deliberate and pre-registered (Phase 1d
prompt): for this family the momentum sign IS the regime question. Price
above its level 30 days ago is itself the "are we trending up?" test;
layering an SMA(200) filter on top would measure the interaction of two
trend signals, not the mechanism. Chassis otherwise unchanged: ATR hard
stop, 1%-risk sizing, one position max, long-only.

Anchoring discipline: lookback defined in DAYS, converted to 4h bars in
init() — 30 days -> 180 bars. The a-priori default of 30 days comes from
the crypto TSMOM literature (1-3 month lookbacks), frozen before any run.

Rules:
  Entry:  momentum crosses from <=0 to >0 at a 4h close -> buy next open.
  Exit:   momentum back to <=0 at a 4h close, or hard stop at
          entry − atr_mult × ATR(14) — whichever comes first.

Strategy versions are immutable once they enter paper mode (BUILD_PLAN).
"""

import math

from backtesting import Strategy

from backtest.config import RISK_PCT
from backtest.indicators import atr, momentum

BARS_PER_DAY = 6  # 4h bars


class TsmomV1(Strategy):
    # Parameters exposed for optimization (training window only).
    lookback_days = 30
    atr_mult = 2.0
    atr_n = 14  # 4h bars
    risk_pct = RISK_PCT

    def init(self):
        lookback_n = self.lookback_days * BARS_PER_DAY  # 30d -> 180 bars
        close = self.data.Close
        self.mom = self.I(momentum, close, lookback_n)
        self.atr_ = self.I(atr, self.data.High, self.data.Low, close, self.atr_n)

    def next(self):
        if self.position:
            if self.mom[-1] <= 0:
                self.position.close()
            return

        # Entry: momentum crosses from <=0 to >0 at this close. Implemented
        # literally (not lib.crossover) so the <=0 boundary is exact; NaN
        # warmup compares False on both sides and blocks entries.
        if len(self.mom) < 2 or not (self.mom[-2] <= 0 < self.mom[-1]):
            return

        price = self.data.Close[-1]
        a = self.atr_[-1]
        if math.isnan(a) or a <= 0:
            return
        stop = price - self.atr_mult * a
        if stop <= 0:
            return
        frac = min(self.risk_pct * price / (price - stop), 0.99)
        self.buy(size=frac, sl=stop)
