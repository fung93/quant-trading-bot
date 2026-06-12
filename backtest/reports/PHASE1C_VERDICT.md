# Phase 1c Verdict — Donchian Breakout (donchian_v1, 4h)

Generated 2026-06-12. Mechanism swap: Turtle-style Donchian channel
breakout inside the unchanged chassis (200-day regime filter, ATR×2 stop,
1%-risk sizing, 0.2%/side fees). No volume gate. Lookbacks day-anchored:
entry 20d = 120 × 4h bars, exit 10d = 60 bars, regime 200d = 1200 bars.
Defaults (20/10/2.0/200) are from the classic Turtle/Donchian literature,
frozen before any backtest ran; validation ran exactly once.

## The verdict in one paragraph

**Weak/uncertain — the first mechanism to earn that label instead of a
rejection.** Donchian passed the test MA-cross failed twice: positive
training expectancy on *both* assets (+3.52% BTC, +1.37% ETH per trade,
after fees), a robustness grid with a genuine stable region (BTC 9/9 cells
positive, ETH 6/9), and — the asymmetry test that killed MA-cross — BTC
and ETH *agreeing* across the 10d and 20d lookback rows. But validation
did not confirm: ETH was positive (+3.95%/trade on just 7 trades) while
BTC, the larger sample, landed at −0.12% on 19 trades — **positive before
fees (+0.28%), negative after.** That sentence is the whole result: if
this mechanism has an edge on BTC, it is currently smaller than the cost
of trading it. No sample anywhere reaches 30 trades, this is the third
family tested (multiple-comparisons discount applies), and the verdict is
*not validated, not rejected: uncertain* — with specific evidence, below,
on what would move it.

## The five required answers

**1. Trade counts / rate.** Validation: 19 (BTC) + 7 (ETH) = 26 trades
over ~29 months ≈ 0.9/month combined — 30 paper trades would take ~3
years, not 3–6 months. Better than MA-cross (6× the activity) but still
~6× short of the Phase 2 evidence-rate bar. Fail on rate.

**2. Training first (pre-registered reading).** Training expectancy was
**positive on both symbols** — BTC +3.52% (13 trades), ETH +1.37% (15) —
so, unlike 1b, validation had something real to confirm. Validation
answered: mixed. ETH +3.95% (7 trades); BTC −0.12% (19 trades). No
regime-luck inversion this time — but no confirmation either. The BTC
result decomposes cleanly: 15.8% win rate × +12.93% avg win vs 84.2% ×
−2.57% avg loss ≈ zero; the fee model (0.40pp/trade, verified below) is
the difference between +0.28% and −0.12%.

**3. vs Buy & Hold.**

| Window | Symbol | Trades | Expectancy | Strategy return | HODL return | Strategy maxDD | HODL maxDD | Time in mkt |
|---|---|---|---|---|---|---|---|---|
| train | BTC | 13 | +3.52% | +18.9% | +45.8% | −5.5% | −77.0% | 18.2% |
| train | ETH | 15 | +1.37% | +3.2% | +210.2% | −12.4% | −81.1% | 17.7% |
| validation | BTC | 19 | −0.12% | −4.7% | +50.2% | −10.7% | −51.9% | 16.3% |
| validation | ETH | 7 | **+3.95%** | +9.6% | **−26.7%** | −6.6% | −67.8% | 9.1% |

Every cell statistically weak (n < 30). The drawdown asymmetry is the
chassis working as designed (−4% to −12% vs HODL's −52% to −81%); ETH
validation is the standout — positive absolute return through a window
where holding lost 27%. It is also only 7 trades.

**4. Robustness / asset agreement.** Grid (training only, 9 cells/symbol):
BTC **9/9 positive** (+1.5% to +4.8%, smooth across rows — a real stable
region, first seen in this lab); ETH **6/9** — the 10d and 20d rows all
positive and in agreement with BTC; only the slow 55d row negative. The
asset-asymmetry pattern that rejected MA-cross does **not** repeat at the
10–20d lookbacks. The 55d disagreement is interpretable rather than
random: ETH's 2021–2023 trends were shorter-lived than a 55-day channel
needs.

**5. Ledger updated; classification: WEAK/UNCERTAIN.** Not validated: the
larger validation sample is at-or-below zero after fees and every sample
is far under 30 trades. Not rejected: it passed training on both assets
with a stable, asset-agreeing parameter region — the exact bar both prior
families missed. Family #3 of the ledger; the pre-registered stopping rule
is **not triggered** (it requires failure on both assets).

## Entry funnel

| Symbol | Window | breakout bars (close > prior 20d high) | + regime (= entry-eligible bars) |
|---|---|---|---|
| BTC | train | 121 | 62 |
| BTC | validation | 126 | 74 |
| ETH | train | 142 | 59 |
| ETH | validation | 111 | 43 |

Eligible bars cluster inside trends, so realized trades (7–19) are far
fewer than eligible bars — one position at a time absorbs a cluster.

## Integrity checks

- **No self-referential breakout:** channels are built from *preceding*
  bars only — `rolling(n).max().shift(1)` in `indicators.prior_high` /
  `prior_low` (acceptance #2).
- **Day-anchored lookbacks:** `entry_n = self.entry_days * BARS_PER_DAY`
  (20d → 120 bars), likewise exit (10d → 60) and regime (200d → 1200), in
  `strategies/donchian_v1.py::init` (acceptance #1).
- **Fees real:** BTC validation re-run with zero fees: +0.28% vs −0.12%
  with fees — exactly the modeled 0.40% round trip per trade.
- **Provenance:** Turtle-literature defaults frozen before any run; grid
  on training only; nothing selected from it; prior strategy files
  untouched (clean git diff).

## What would move this verdict (evidence, not recommendation)

Uncertain means: specify what would decide it. Three observations the
data itself suggests — each would be a pre-registered future experiment,
none is a recommendation to trade:

1. **The fee line is the battleground.** BTC validation flips sign on
   fees alone. Any venue/fee assumption change (or a mechanism tweak that
   cuts trade count while keeping winners) directly decides this.
2. **The 10d/5d row was the grid's most active and consistent cell block**
   (19–23 trades, positive on both assets). A pre-registered 10d variant
   would roughly double the evidence rate — closer to Phase 2's
   20–30-trades-in-months requirement.
3. **Time-series momentum (ledger #4)** remains the planned sibling test;
   if it also lands weak-positive, the trend-following picture firms up;
   if it fails on both assets, the stopping rule fires for new variants.

No trading — paper or live — is recommended from anything in this report.
