"""Single source of truth for backtest assumptions (Phase 1 hard rule #1).

Change venue assumptions here and nowhere else.
"""

# Spot assumption: 0.1% fee + 0.1% slippage per side = 0.4% round trip.
FEE_PER_SIDE = 0.001
SLIPPAGE_PER_SIDE = 0.001

# backtesting.py's `commission` is charged on every fill (entry and exit),
# so per-side fee + slippage map directly onto it.
COMMISSION_PER_SIDE = FEE_PER_SIDE + SLIPPAGE_PER_SIDE

# Risk per trade: a stop-out loses 1% of current equity (BUILD_PLAN rule 5).
RISK_PCT = 0.01

# backtesting.py sizes positions in whole units. With cash this large, one
# unit of BTC (~1e5) is ~0.0001% of equity, so whole-unit rounding is
# negligible. This is the stated workaround for sizing granularity.
CASH = 100_000_000

# Train/validation split (Phase 1 hard rule #3). Parameter selection on
# TRAIN only; validation runs ONCE per strategy with frozen parameters.
TRAIN = ("2021-01-01", "2023-12-31")
VALIDATION = ("2024-01-01", None)  # None = latest available

SYMBOLS = ["BTCUSDT", "ETHUSDT"]

# Metrics from fewer trades than this are flagged "statistically weak".
MIN_TRADES = 30
