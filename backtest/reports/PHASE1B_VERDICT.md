# Phase 1b Verdict — ma_cross on 4h Candles

Generated 2026-06-12. One controlled change vs Phase 1: decision timeframe
daily → 4h (`ma_cross_v1_4h`). Regime filter deliberately kept at the
200-DAY scale — `regime_n = 1200` (1200 × 4h = 200 days) — so "are we in a
bull market?" did not silently become a 33-day question. All other logic,
fees (0.2%/side), sizing (1% risk), and the train/validation split are
identical to Phase 1. Validation ran once, with the a-priori defaults
(20/50, 200-day regime, ATR×2.0) frozen before it ran.

## The verdict in one paragraph

**The experiment worked; the strategy still doesn't.** Moving to 4h fixed
exactly what it was supposed to fix — signal frequency rose ~6× (40 gated
entries vs 6 in Phase 1) — so sample starvation is no longer hiding the
answer. The answer it stopped hiding: **this gate structure has no
demonstrated edge.** It *lost* on the training window on both symbols with
the default parameters, and on ETH it lost on **all twelve** robustness
combinations. The positive validation numbers (BTC +2.84%/trade on 11
trades, ETH +1.54% on 5) cannot be read as an out-of-sample pass — a
strategy that fails its own training window has nothing for validation to
confirm; what remains is a small, statistically weak sample that happened
to land in friendlier 2024–2026 trend conditions. Classification:
**rejected for promotion** (as a Phase 2 candidate in current form), with
the family-level finding below worth more than the rejection itself.

## The three questions the experiment was built to answer

**1. Did 4h produce ≥30 validation trades, or a rate that reaches 30 paper
trades in 3–6 months?  No — not close.** Validation produced 11 (BTC) + 5
(ETH) trades over ~29 months ≈ 0.55 trades/month combined. Thirty paper
trades at that rate takes ~4.5 years. Reaching 30 in 6 months needs ~9×
more signals. The 6× frequency gain from 1d→4h was real but the gates
(regime + cross + volume) remain the binding constraint.

**2. Is validation expectancy positive after fees, and how does it compare
to HODL?  Positive but unattributable.** BTC validation: +2.84%/trade,
+11.3% total vs HODL +50.2% — far less return, but with −3.3% max drawdown
vs HODL's −51.9%. ETH validation: +1.54%/trade, +1.7% vs HODL −26.7%
(drawdown −4.1% vs −67.8%). On a pure drawdown-adjusted view these look
attractive — but they sit on 16 trades total, *and* the same frozen
parameters produced **negative** training expectancy (BTC −0.35%, ETH
−4.19%, including an 11-trade, zero-win streak on ETH). Positive
out-of-sample after negative in-sample is the signature of regime luck,
not edge.

**3. Does the robustness grid now show a stable region?  The instability
moved, it didn't disappear.** With real samples per cell (2–24 trades),
signs no longer flip between adjacent parameter cells — they flip between
*assets*: BTC training grid 10/12 positive (with the default 20/50 cell
among the negatives), ETH training grid **0/12 positive**. A structural
edge in a strategy family should not vanish entirely on the second asset.
Per the pre-registered standard in the prompt: **the MA-cross family
itself looks weak on these assets** — its results are driven by
asset-specific regime sequences, not by a repeatable mechanism the
parameters merely tune.

## Results table

| Window | Symbol | Trades | Expectancy/trade | Win rate | Strategy return | HODL return | Strategy maxDD | HODL maxDD | Time in mkt |
|---|---|---|---|---|---|---|---|---|---|
| train | BTC | 13 | −0.35% | 15.4% | −5.6% | +45.8% | −10.9% | −77.0% | 5.2% |
| train | ETH | 11 | −4.19% | 0.0% | −11.5% | +210.2% | −11.5% | −81.1% | 2.1% |
| validation | BTC | 11 | **+2.84%** | 63.6% | +11.3% | +50.2% | −3.3% | −51.9% | 8.4% |
| validation | ETH | 5 | +1.54% | 60.0% | +1.7% | −26.7% | −4.1% | −67.8% | 4.0% |

Every row **statistically weak** (n < 30). Full per-run reports and equity
curves alongside this file; robustness table in
`robustness_ma_cross_v1_4h.md`.

## Entry funnel (the experiment's other half)

| Symbol | Window | raw cross-ups | + regime | + volume gate |
|---|---|---|---|---|
| BTC | train | 74 | 25 | 13 |
| BTC | validation | 62 | 26 | 11 |
| ETH | train | 74 | 30 | 11 |
| ETH | validation | 62 | 17 | 5 |

vs Phase 1 daily funnel (BTC train: 12 → 3 → 1). The volume gate still
removes ~50–70% of regime-passing signals at 4h, as it did on daily.

## Integrity checks

- **Resample fidelity:** 8 sampled 4h candles (including two spanning a
  known exchange outage) match Binance's native 4h klines exactly on
  O/H/L/C/V (`backtest/verify_resample.py`, repeatable).
- **Regime scale:** `regime_n = 1200    # 4h bars = 200 DAYS` in
  `strategies/ma_cross_v1_4h.py` — the daily-scale anchor, as specified.
- **Fees real:** zero-fee rerun of BTC validation: +3.24% vs +2.84% with
  fees — the modeled 0.40% round trip is present per trade.
- **No lookahead / sizing:** unchanged machinery from Phase 1, verified
  there (next-open fills, 1%-risk math).
- **Provenance:** defaults frozen before validation; robustness grid ran
  on training only; nothing was selected from it; `ma_cross_v1.py`
  untouched (clean git diff).

## What this redirects (evidence, not recommendation)

The constructive output of 1b is family-level: timeframe was not the
problem, and parameters are not the problem — the *mechanism* (MA cross
gated by volume inside a 200-day regime) does not show a repeatable edge
on BTC/ETH after fees. Future hypotheses should change the mechanism, not
its knobs: e.g. different entry logic inside the same regime/risk
framework, or a different signal family entirely. Each would be a new
strategy version through this same lab. No trading — paper or live — is
recommended from anything in this report.
