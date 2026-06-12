"""rsi_revert_v1 — RSI mean-reversion (Phase 1 reference strategy).

Long-only: buy dips in uptrends, never falling knives.
  Entry:  RSI(14) crosses below entry threshold (30) while Close > SMA(200).
  Stop:   signal close − atr_mult × ATR(14), hard stop.
  Exit:   RSI crosses above exit threshold (55), stop hit, or regime fails.
Entry at next open (backtesting.py default — no lookahead). Sizing:
risk-based — a stop-out loses risk_pct of current equity, capped at 99%.

Strategy versions are immutable once they enter paper mode (BUILD_PLAN).
"""

import math

from backtesting import Strategy
from backtesting.lib import crossover

from backtest.config import RISK_PCT
from backtest.indicators import atr, rsi, sma


class RsiRevertV1(Strategy):
    # Parameters exposed for optimization (training window only).
    rsi_n = 14
    entry_th = 30
    exit_th = 55
    regime_n = 200
    atr_mult = 2.0
    atr_n = 14
    risk_pct = RISK_PCT

    def init(self):
        close = self.data.Close
        self.rsi_ = self.I(rsi, close, self.rsi_n)
        self.regime_ma = self.I(sma, close, self.regime_n)
        self.atr_ = self.I(atr, self.data.High, self.data.Low, close, self.atr_n)

    def next(self):
        price = self.data.Close[-1]
        regime_ok = price > self.regime_ma[-1]

        if self.position:
            if crossover(self.rsi_, self.exit_th) or not regime_ok:
                self.position.close()
            return

        if not regime_ok:
            return
        if not crossover(self.entry_th, self.rsi_):  # RSI crossed below threshold
            return

        a = self.atr_[-1]
        if math.isnan(a) or a <= 0:
            return
        stop = price - self.atr_mult * a
        if stop <= 0:
            return
        frac = min(self.risk_pct * price / (price - stop), 0.99)
        self.buy(size=frac, sl=stop)
