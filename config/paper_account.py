"""Paper account parameters (Phase 2) - single source of truth.

Owner-confirmed 2026-06-12. The account runs in USD because the venue
quotes in USDC. The paper book = ETH (primary) trades only; BTC
observational trades are recorded but never touch equity or the kill
switch, so observational noise cannot suppress the primary book.
"""

INITIAL_CAPITAL_USD = 230.0   # ~ RM1,000

# Display only - NEVER used in accounting. Refresh manually if it drifts.
MYR_PER_USD = 4.35

# 1% of current equity at risk per stop-out (~$2.30 at start).
RISK_PER_TRADE = 0.01

# Peak-to-trough drawdown on paper equity that halts NEW entries (exits
# still managed). Manual reset only - see README.
KILL_SWITCH_DD = 0.10

# Position = risk / stop-distance, capped at 95% of current equity
# (spot, no leverage; a small-ATR signal must never imply >100% exposure).
MAX_POSITION_PCT = 0.95

# Fee model: imported from the lab's measured constants (0.10%/side).
from backtest.config import FEE_PER_SIDE, SLIPPAGE_PER_SIDE  # noqa: E402,F401

COST_PER_SIDE = FEE_PER_SIDE + SLIPPAGE_PER_SIDE  # 0.001 = 0.10% per side
