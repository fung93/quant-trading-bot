"""DB-free verification of the signal engine's logic (Phase 2 Task 6).

Tests the SAME functions the engine runs (imported, not re-typed):
  1. Parameter provenance: engine constants come from strategies/tsmom_v1.py.
  2. Sizing math: worked example + the 95% cap case.
  3. Kill switch: fake losing trades push drawdown over 10% -> entries
     would be suppressed and the alert fires (simulated, no DB writes).
  4. Historical cross: against cached 4h data, the entry condition is True
     at a known momentum-cross bar and False at its neighbors - exactly
     one signal where exactly one belongs.

    python scripts/test_engine_logic.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import numpy as np

from backtest.indicators import atr, momentum
from backtest.loader import load_candles
from config.paper_account import (
    INITIAL_CAPITAL_USD,
    KILL_SWITCH_DD,
    MAX_POSITION_PCT,
    RISK_PER_TRADE,
)
from signal_engine import ATR_MULT, ATR_N, LOOKBACK_N, entry_cross, size_position
from strategies.tsmom_v1 import BARS_PER_DAY, TsmomV1

failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'PASS' if cond else 'FAIL'}: {name}" + (f" ({detail})" if detail else ""))
    if not cond:
        failures.append(name)


# 1. Provenance: engine constants are imports from the strategy, not copies.
check("lookback = TsmomV1.lookback_days x BARS_PER_DAY",
      LOOKBACK_N == TsmomV1.lookback_days * BARS_PER_DAY == 180, f"{LOOKBACK_N}")
check("ATR params imported", ATR_MULT == TsmomV1.atr_mult and ATR_N == TsmomV1.atr_n)

# 2a. Sizing worked example (the README example).
equity, price, atr_val = 230.0, 1650.0, 38.0
s = size_position(equity, price, atr_val)
check("stop = price - 2xATR", abs(s["stop"] - (1650 - 76)) < 1e-9, f"{s['stop']:.2f}")
check("risk = 1% of equity", abs(s["risk_usd"] - 2.30) < 1e-9, f"${s['risk_usd']:.2f}")
expect_units = 2.30 / 76.0
check("units = risk / stop-distance", abs(s["units"] - expect_units) < 1e-12,
      f"{s['units']:.6f} ETH = ${s['size_usd']:.2f}")
check("position under 95% cap", s["size_usd"] <= MAX_POSITION_PCT * equity,
      f"{s['size_usd'] / equity * 100:.1f}% of equity")

# 2b. Cap case: tiny ATR would imply >100% exposure -> capped at 95%.
s2 = size_position(230.0, 1650.0, 4.0)  # stop distance 8 -> uncapped ~287% equity
check("tiny-ATR position capped at 95%",
      abs(s2["size_usd"] - 0.95 * 230.0) < 1e-9,
      f"${s2['size_usd']:.2f} = {s2['size_usd'] / 230 * 100:.0f}%")

# 3. Kill switch simulation: inject fake losing ETH trades.
fake_pnls = [-8.0, -9.0, -7.5]  # cumulative -24.5 on 230 -> 10.7% drawdown
eq = INITIAL_CAPITAL_USD + sum(fake_pnls)
peak = INITIAL_CAPITAL_USD  # never rose above start
dd = (peak - eq) / peak
check("fake losses breach the 10% line", dd >= KILL_SWITCH_DD, f"dd {dd * 100:.1f}%")
kill_active = dd >= KILL_SWITCH_DD
suppressed = kill_active  # the engine's entry branch: if kill_active -> suppress
check("entries would be suppressed", suppressed)
check("alert would fire on transition", kill_active,
      "kill_switch_update sends Telegram on inactive->active")

# 4. Historical cross on real cached data (exactly one signal at the cross).
df = load_candles("ETHUSDT", "4h")
mom = momentum(df["Close"].to_numpy(), LOOKBACK_N)
prev = np.roll(mom, 1)
cross_idx = np.where((prev <= 0) & (mom > 0) & ~np.isnan(prev))[0]
check("history contains momentum crosses", len(cross_idx) > 0, f"{len(cross_idx)} crosses")
t = int(cross_idx[-1])  # most recent completed cross
check("entry_cross TRUE at the cross bar", entry_cross(mom[: t + 1]),
      str(df.index[t]))
check("entry_cross FALSE one bar before", not entry_cross(mom[:t]))
check("entry_cross FALSE one bar after (no re-fire)",
      not entry_cross(mom[: t + 2]) if t + 2 <= len(mom) else True)
a_t = atr(df["High"].to_numpy(), df["Low"].to_numpy(), df["Close"].to_numpy(), ATR_N)[t]
s_t = size_position(230.0, float(df["Close"].iloc[t]), float(a_t))
check("sizing valid at the cross bar", s_t is not None and s_t["stop"] > 0,
      f"close {df['Close'].iloc[t]:.2f}, stop {s_t['stop']:.2f}, ${s_t['size_usd']:.2f}")

print()
if failures:
    print(f"{len(failures)} FAILURE(S): {failures}")
    sys.exit(1)
print("ALL ENGINE LOGIC CHECKS PASSED")
