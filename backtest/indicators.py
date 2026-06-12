"""Indicator helpers for use inside backtesting.py's self.I(...).

Each takes raw arrays and returns a numpy array aligned to the input, with
NaN during the warmup period. RSI and ATR use Wilder smoothing
(ewm alpha=1/n), the textbook definitions.
"""

import numpy as np
import pandas as pd


def sma(values, n: int) -> np.ndarray:
    return pd.Series(np.asarray(values, dtype=float)).rolling(n).mean().to_numpy()


def rsi(values, n: int = 14) -> np.ndarray:
    s = pd.Series(np.asarray(values, dtype=float))
    delta = s.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    out = 100 - 100 / (1 + gain / loss)
    out = out.where(loss != 0, 100.0)  # straight-up move: RSI pegs at 100
    return out.to_numpy()


def atr(high, low, close, n: int = 14) -> np.ndarray:
    h = pd.Series(np.asarray(high, dtype=float))
    l = pd.Series(np.asarray(low, dtype=float))
    c = pd.Series(np.asarray(close, dtype=float))
    prev_close = c.shift(1)
    tr = pd.concat(
        [h - l, (h - prev_close).abs(), (l - prev_close).abs()], axis=1
    ).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False, min_periods=n).mean().to_numpy()
