"""donchian_v1 — Donchian channel breakout on 4h candles (Phase 1c).

Mechanism swap: 1b rejected the MA-cross family while the chassis (regime
filter, ATR stop, 1%-risk sizing) behaved as designed. This strategy keeps
the chassis and replaces the engine with classic Turtle-style breakout
logic. No volume gate (1b showed it deleting 50-70% of signals inside
mechanisms that lost anyway).

Anchoring discipline (as in 1b): all lookbacks are defined in DAYS and
converted to 4h bars in init() — 6 bars per day:
    entry channel  20 days -> 120 bars
    exit channel   10 days ->  60 bars
    regime SMA    200 days -> 1200 bars
The channels use ONLY preceding bars (rolling max/min shifted by one, see
indicators.prior_high/prior_low) so a close can never break out over its
own bar's high.

Rules (long-only, one position max):
  Regime:  Close > 200-day SMA; no entries below it, open position closes
           if it fails.
  Entry:   4h close strictly above the prior 20-day high -> buy next open.
  Stop:    signal close − atr_mult × ATR(14) on 4h bars, hard stop.
  Exit:    4h close below the prior 10-day low (channel exit), or stop,
           or regime failure — whichever comes first.
  Sizing:  a stop-out loses risk_pct of current equity, capped at 99%.

A-priori defaults (20/10/2.0/200) come from the classic Turtle/Donchian
literature, chosen before any backtest ran. Strategy versions are
immutable once they enter paper mode (BUILD_PLAN).
"""

import math

from backtesting import Strategy

from backtest.config import RISK_PCT
from backtest.indicators import atr, prior_high, prior_low, sma

BARS_PER_DAY = 6  # 4h bars


class DonchianV1(Strategy):
    # Parameters exposed for optimization (training window only) - in DAYS.
    entry_days = 20
    exit_days = 10
    regime_days = 200
    atr_mult = 2.0
    atr_n = 14  # 4h bars
    risk_pct = RISK_PCT

    def init(self):
        # Day-anchored lookbacks converted to 4h bars (acceptance check 1).
        entry_n = self.entry_days * BARS_PER_DAY    # 20d -> 120 bars
        exit_n = self.exit_days * BARS_PER_DAY      # 10d -> 60 bars
        regime_n = self.regime_days * BARS_PER_DAY  # 200d -> 1200 bars

        close = self.data.Close
        self.entry_high = self.I(prior_high, self.data.High, entry_n)
        self.exit_low = self.I(prior_low, self.data.Low, exit_n)
        self.regime_ma = self.I(sma, close, regime_n)
        self.atr_ = self.I(atr, self.data.High, self.data.Low, close, self.atr_n)

    def next(self):
        price = self.data.Close[-1]
        # NaN warmup compares False -> entries stay blocked.
        regime_ok = price > self.regime_ma[-1]

        if self.position:
            if (not regime_ok) or price < self.exit_low[-1]:
                self.position.close()
            return

        if not regime_ok:
            return
        if not price > self.entry_high[-1]:  # strictly above prior 20-day high
            return

        a = self.atr_[-1]
        if math.isnan(a) or a <= 0:
            return
        stop = price - self.atr_mult * a
        if stop <= 0:
            return
        frac = min(self.risk_pct * price / (price - stop), 0.99)
        self.buy(size=frac, sl=stop)
