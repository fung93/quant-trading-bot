# Phase 1 Verdict — Backtesting Lab Results

Generated 2026-06-12. Data: Binance daily candles, 2021-01-01 → 2026-06-11.
Fees modeled throughout: 0.2% per side (0.4% round trip). Train window
2021-01-01 → 2023-12-31; validation 2024-01-01 → 2026-06-11. Validation was
run exactly once per strategy, with parameters frozen before it ran.

## The verdict in one paragraph

**Neither reference strategy produced a validated edge — but not because
they lost money. They barely traded at all.** Across two strategies, two
symbols, and five and a half years, the rules fired a grand total of **6
trades** (the 30-trade minimum for statistical meaning was missed by an
order of magnitude on every single run). With samples this small, every
expectancy number on this page — positive or negative — is noise. The
honest conclusion is "insufficient evidence", and under our own rules
(BUILD_PLAN: never conclude from fewer than 30 trades) both strategies are
**rejected for promotion to Phase 2 in their current form**. The clean
negative result is itself the Phase 1 deliverable: the lab works, the
method is sound, and these particular gate structures are too strict to
generate evidence on daily candles.

## Results table

| Strategy | Symbol | Window | Trades | Expectancy/trade | Strategy return | HODL return | Strategy maxDD | HODL maxDD |
|---|---|---|---|---|---|---|---|---|
| ma_cross_v1 | BTC | train | 1 | −5.18% | −0.55% | +46.19% | −2.49% | −76.63% |
| ma_cross_v1 | BTC | validation | 1 | −9.05% | −1.04% | +50.47% | −1.04% | −51.16% |
| ma_cross_v1 | ETH | train | 2 | +6.73% | +1.16% | +209.86% | −3.68% | −79.30% |
| ma_cross_v1 | ETH | validation | 0 | n/a | 0.00% | −26.66% | 0.00% | −67.52% |
| rsi_revert_v1 | BTC | train | 1 | +17.98% | +2.13% | +46.19% | −0.15% | −76.63% |
| rsi_revert_v1 | BTC | validation | 1 | −8.08% | −1.05% | +50.47% | −1.05% | −51.16% |
| rsi_revert_v1 | ETH | train | 0 | n/a | 0.00% | +209.86% | 0.00% | −79.30% |
| rsi_revert_v1 | ETH | validation | 0 | n/a | 0.00% | −26.66% | 0.00% | −67.52% |

Every row: **statistically weak** (n < 30). Full per-run reports with equity
curves sit alongside this file.

## Classification (per the three required categories)

- **Validated edge: none.** No strategy/symbol combination has positive
  validation expectancy with a meaningful sample.
- **Weak/uncertain: everything that traded.** ma_cross_v1 on ETH (train)
  and rsi_revert_v1 on BTC (train) show positive numbers from 1–2 trades —
  exactly the kind of result that looks like an edge and is actually an
  anecdote.
- **Rejected (for promotion, in current form): both strategies.** Not
  proven harmful — proven *unable to generate evidence*. A strategy that
  fires once every 2–3 years cannot pass a 30-trade bar within any
  reasonable paper-trading horizon, so it cannot ever clear the Phase 3
  gate. Structural, not parametric: see robustness below.

## Why so few trades (measured, not guessed)

For ma_cross_v1 on the training window the entry funnel was: BTC — 12 raw
SMA20/50 cross-ups → 3 survive the regime filter (Close > SMA200) → **1**
survives the volume gate. ETH — 11 → 5 → **2**. The volume condition
(candle volume above its 20-day average on the exact crossover day) removes
about two-thirds of already-rare signals.

For rsi_revert_v1 the regime filter and the entry condition are close to
mutually exclusive on daily candles: by the time RSI(14) is below 30,
price is almost always already below the 200-day average — on ETH the
overlap was exactly zero in both windows.

## Robustness grid (anti-overfitting check, training window only)

12 parameter combinations per symbol (see robustness_ma_cross_v1.md):
BTC 6/12 cells positive, ETH 9/12, trade counts 1–4 everywhere. Expectancy
flips sign between adjacent combinations (BTC: 20/50 −5.2%, 20/100 +10.5%,
50/200 −6.6%). **No stable region exists**; the standout 20/100 column is
the textbook one-hot-cell overfitting warning the method exists to catch.
Per the rules, no combination was selected.

## Parameter provenance (audit trail)

Defaults (20/50/200 MAs, RSI 14/30/55, ATR×2.0, 1% risk) came from
BUILD_PLAN.md, written before any backtest ran. The robustness grid ran on
training data only. No parameter was changed in response to any result,
and validation ran once with the a-priori defaults. There was no tuning
loop — nothing to leak.

## Integrity checks performed

- **No lookahead:** every recorded entry fills at the candle *after* the
  signal, at that candle's open (verified programmatically against raw data).
- **Fees real:** re-running with fees zeroed improves expectancy by ~0.39pp
  per trade — the modeled 0.4% round trip is demonstrably in the results.
- **Sizing:** stop-distance-based, 1% of equity at risk per stop-out;
  equity impact of the losing BTC trade matched the math.

## What this means for Phase 2 (evidence, not recommendation)

Phase 2 needs a strategy that trades often enough to log 20–30 paper
trades in months, not decades. These two reference implementations cannot.
Next candidates must be **new versions** (e.g. `ma_cross_v2`) per the
immutability convention — plausible directions the evidence suggests:
drop or soften the volume gate, widen the RSI entry threshold, or move to
the 4h timeframe (×6 the candles). All would go through this same lab,
same split, same rules. No live or paper trading is recommended from
anything in this report.
