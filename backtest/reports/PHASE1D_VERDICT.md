# Phase 1d Verdict — Measured Fees + Time-Series Momentum

Generated 2026-06-12. Three jobs: adopt the measured fee model (0.10%/side,
Sushi/Katana, audit trail in EXPERIMENT_LEDGER.md), re-score Donchian under
it (PHASE1C_RESCORE.md), and run time-series momentum as pre-registered
ledger family #4. TSMOM defaults (30-day lookback = 180 × 4h bars, ATR×2.0,
no regime gate — the momentum sign IS the regime, per the pre-registered
design) frozen from crypto TSMOM literature before any run. Validation ran
once. Training stated first throughout.

## The verdict in one paragraph

**This is the first experiment to produce statistically meaningful
samples, and the first cell that meets every pre-registered criterion for
a validated edge.** TSMOM traded 80–102 times per cell — no weak-sample
flags anywhere, a first. Training: +1.40% (BTC, 82 trades) and +1.46%
(ETH, 102) per trade after measured fees — nearly identical across assets.
Validation: **ETH +1.63% on 80 trades** — positive training, frozen
parameters, adequate sample, stable grid, asset-agreeing structure: every
box ticked. BTC validation: −0.09% on 90 trades — flat; BTC 2024–2026
gave trend-followers nothing after costs, and *both* independent
mechanisms (Donchian re-scored, TSMOM) say exactly that. The convergence
question resolves YES: two unrelated trend engines tell one coherent
story — trend-following on these assets is real but thin, alive on ETH
out-of-sample, dead-flat on BTC's recent regime. Classification: TSMOM
**weak-positive overall; its ETH validation cell is the lab's first
individually validated result** — read with the multiple-comparisons
discount a 4th family deserves. The stopping rule did not fire, decisively.

## The six required answers

**1. Trade counts / rate — PASS, first time.** Validation: 90 (BTC) + 80
(ETH) = 170 trades over ~29 months ≈ 5.8/month across both symbols. Thirty
paper trades arrive in ~5 months (≈10 months on one symbol alone) — inside
the 3–6 month bar that every prior strategy missed by 6–10×.

**2. Training first, then validation (measured fees).** Training: BTC
+1.40%/trade (82), ETH +1.46% (102) — positive, consistent, real samples.
Validation: ETH **+1.63%** (80) — confirms training. BTC **−0.09%** (90) —
flat; +0.11% before fees, so even at measured costs the recent BTC regime
offers less per trade than one round trip. No regime-luck inversion
(training was positive); the BTC result is a *non-confirmation on one
asset*, not a luck artifact.

**3. vs Buy & Hold.**

| Window | Symbol | Trades | Expectancy | Strategy return | HODL return | Strategy maxDD | HODL maxDD | Time in mkt |
|---|---|---|---|---|---|---|---|---|
| train | BTC | 82 | +1.40% | **+50.7%** | +45.8% | −9.3% | −77.0% | 38.7% |
| train | ETH | 102 | +1.46% | +41.4% | +210.2% | −17.7% | −81.1% | 42.7% |
| validation | BTC | 90 | −0.09% | +1.8% | +50.2% | −23.1% | −51.9% | 36.5% |
| validation | ETH | 80 | **+1.63%** | **+50.7%** | **−26.7%** | −16.6% | −67.8% | 40.7% |

Two standouts: BTC train is the lab's first outright HODL beat on return
(+50.7% vs +45.8%) with one-eighth the drawdown; ETH validation made
+50.7% through a window where holding lost 26.7%. The mirror image: BTC
validation trailed HODL badly (+1.8% vs +50.2%) — the cost of trading a
trendless regime.

**4. Robustness and asset agreement — the strongest grid yet.** BTC 8/9
positive, ETH 6/9, on 40–170 trades per cell. More important than the
counts: the **shape agrees across assets** — 30d is the sweet spot on both
(+1.4% to +2.0%), 14d weakly positive on both, 90d ≈ dead on both. A
smooth, asset-consistent gradient peaking at the a-priori literature
default is what a real-but-modest effect looks like; the one-hot-cell and
asset-asymmetry patterns that killed MA-cross are absent.

**5. Convergence — YES.** Donchian (re-scored: all four cells positive,
BTC validation +0.08%) and TSMOM (three of four positive, BTC validation
−0.09%) are independent mechanisms agreeing on every structural point:
positive training both assets, ETH validating, BTC 2024–2026 flat within
±one round-trip of zero. Two weak-positives across different mechanisms —
the pre-registered stronger-evidence condition — is what we have.

**6. Ledger updated; stopping rule NOT fired** — it required both families
to fail on both assets; instead both passed training on both assets and
one produced a validated cell. Trend-following on BTC/ETH at 4h survives
the measured fee model.

## Integrity checks

- **Fee model:** constants updated with full audit comment (previous
  value, measured values, method, date, safety margin, pre-commitment);
  ledger entry written. Zero-fee rerun of BTC validation: +0.11% vs
  −0.09% — exactly the 0.20% measured round trip, proving the new model
  is live in results.
- **Re-score purity:** Donchian trade sequences verified identical under
  both fee models, trade-by-trade (entry/exit bars) — re-scored, not
  re-run differently (PHASE1C_RESCORE.md).
- **Day-anchoring:** `lookback_n = self.lookback_days * BARS_PER_DAY`
  (30d → 180 bars) in `strategies/tsmom_v1.py::init`.
- **No regime gate:** deliberate, pre-registered, rationale in the
  docstring — momentum's sign is the regime question for this family.
- **Boundary-exact entry:** `mom[-2] <= 0 < mom[-1]` implemented
  literally per spec.
- **Provenance:** 30d/ATR×2.0 frozen from literature before any run; grid
  on training only, nothing selected from it; all four prior strategy
  files untouched (clean git diff).

## Classification and updated lab position

- **tsmom_v1: weak-positive.** The ETH validation cell (+1.63%, n=80,
  after measured fees, frozen params, confirmed training, stable
  asset-agreeing grid) is the **first result in this lab to satisfy every
  pre-registered validation criterion.** The BTC cell is flat. As family
  #4, a multiple-comparisons discount applies — the proper response to
  which is fresh out-of-sample evidence, i.e. paper trading, not more
  backtests.
- **donchian_v1: weak/uncertain** (unchanged by re-score; all cells
  positive but all n<30).
- **MA-cross family: rejected** (unchanged).
- **Overall:** the lab's central question — "is there an exploitable edge
  after fees at this capital size?" — has moved from "no evidence" to
  "one validated cell plus convergent weak-positives." Per BUILD_PLAN,
  the natural next step is **Phase 2 paper trading of tsmom_v1**
  (ETH primary, BTC observational), which is itself the out-of-sample
  test that decides whether this survives contact with live candles.
  That is a decision for the owner, not this report. No live trading is
  recommended from anything here.
