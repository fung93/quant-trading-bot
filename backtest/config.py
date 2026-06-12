"""Single source of truth for backtest assumptions (Phase 1 hard rule #1).

Change venue assumptions here and nowhere else.
"""

# Fee model revision (2026-06-12) - measurement-driven, not tuned:
#   Previous: 0.001 fee + 0.001 slippage per side = 0.4% round trip,
#   a-priori spot assumption from BUILD_PLAN, used in Phases 1, 1b, 1c.
#   Measured: execution venue decided (Sushi spot on Katana, V3 0.05%
#   fee-tier pools); live round-trip quotes on 2026-06-12 at $1,000 size:
#   USDC<->WETH 0.152% RT, USDC<->WBTC 0.146% RT; gas negligible.
#   Adopted: 0.10% per side (0.20% RT) - measured ~0.15% plus a safety
#   margin for liquidity thinning. Pre-commitment: a WORSE measurement
#   would equally have been adopted. Audit trail: EXPERIMENT_LEDGER.md.
FEE_PER_SIDE = 0.0005
SLIPPAGE_PER_SIDE = 0.0005

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
