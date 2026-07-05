# Go-Live Benchmark — pre-registered criteria for risking real capital

**Frozen 2026-07-05, before the evidence exists.** At the moment of writing:
1 ETH paper trade open, 0 closed, paper equity ~$230. No outcome data yet —
which is exactly why the bar is being set now. Defining "success" after
seeing results is the goalpost-moving this whole project has been built to
resist (frozen parameters, validation run once, the ledger's stopping rule).
This document is that discipline applied to the largest decision left:
whether to move `tsmom_v1` from paper to real money.

Committed to git so it is timestamped and cannot be quietly edited later —
see the Amendment rule at the end.

## Prime directive

**"No edge after fees" is a valid, and likely, outcome — and it is a
success.** The purpose of paper trading is to *earn the right* to risk real
money, or to prove you shouldn't. This bar exists to defend the decision
against your own future greed (a few green trades whispering *go*) and your
own future fear (a drawdown whispering *quit*). Read this at the moment you
are most tempted to override it — that is the moment it is for.

## The metric — expectancy, not win rate

Per BUILD_PLAN's first principle: **expectancy over win rate, always.**
`tsmom_v1` wins only ~26% of the time and is still positive because the
average win dwarfs the average loss. A *high* win rate would be out of
character — mild cause for suspicion, not comfort. The number that decides
this is:

> **expectancy per trade after fees = (win% × avg win) − (loss% × avg loss)**

Backtest baseline (ETH validation 2024-01..2026-06, 80 trades, measured
0.10%/side fees): **+1.63%/trade**, 26% win rate, avg win +11.6% vs avg loss
−1.9%, max drawdown far below buy-and-hold. That is the reference the live
sample is measured against — a plausible *thin* edge, from the 4th mechanism
tested (multiple-comparisons discount applies), not a strong one.

## GO criteria — ALL must hold

1. **Sample:** ≥ 30 closed **ETH** trades, each logged honestly (see #7).
   BTC observational trades are supporting context only and do **not** count
   toward the 30 — BTC is the asset where the edge is expected to be ~zero.
2. **Duration & adversity:** ≥ 3 months elapsed **and** the period contains
   at least one ETH price drawdown of ≥ 20% (crypto routinely delivers
   these). The strategy's whole claim is downside protection; it must be
   tested in a real decline, not an up-only stretch. Realistically, at
   ~2.8 ETH signals/month, reaching 30 trades takes **~9–12 months** — the
   trade count, not the calendar, is the binding constraint.
3. **Expectancy:** mean expectancy per trade after fees **≥ +0.5%** over the
   ≥30 trades. (Comfortably positive, but a conservative fraction of the
   +1.63% backtest — leaving margin for the multiple-comparisons discount
   and real-world fill degradation.)
4. **Not one lucky tail:** drop the single largest winning trade; mean
   expectancy over the remaining trades is still **≥ 0**. If one outlier
   carries the whole result, it is not an edge.
5. **Beats buy-and-hold, risk-adjusted,** over the same period: higher
   return, or comparable return at materially smaller max drawdown.
6. **Survived the drawdown** of criterion 2 without abandoning the rules,
   and the strategy's equity drawdown was materially smaller than HODL's
   over that decline.
7. **Execution integrity:** every fill logged at a faithful price near
   signal time — no hindsight chasing. A sample corrupted by undisciplined
   logging is void, however good the numbers look.

## KILL criteria — ANY one voids the case (in current form)

- Mean expectancy after fees ≤ 0 across ≥ 30 trades.
- Fails the drop-the-best-trade test (edge is a single outlier).
- Kill switch (−10% paper drawdown) triggered → mandatory Phase 3 review,
  never an automatic go.
- Expectancy positive but < +0.5%/trade after 30 trades → not cleared;
  stay in paper or retire the version. Do not lower this bar to fit the
  result.
- Any hard precondition below unmet.

A kill is not failure. It is the method returning an honest answer, which is
the entire point of Phases 1–3.

## Hard preconditions — independent of performance

These must be resolved **before any real capital**, no matter how good the
numbers are:

- **Legal:** confirm the venue and instrument are lawful for a Malaysian
  retail resident — **spot on Katana, NOT perpetuals** (crypto derivatives
  are the highest-risk element regulatorily) — or obtain professional advice
  first. See the compliance review.
- **Tax:** record-keeping in place; understand that systematic trading gains
  may be taxable as income in Malaysia (badges of trade).
- **Dry-run:** Phase 4's mandated 2 weeks of dry-run (logging intended
  orders without sending) completed with no execution errors.
- **Capital:** only true risk capital (~RM50–100 per position per
  BUILD_PLAN) — money you can lose in full without it mattering.

## What "GO" actually means

Not "scale up." It means: proceed to Phase 4's dry-run → then live at
**minimum size** → one month with no execution errors → *only then* is
scaling even a conversation. Real capital is itself another experiment —
it tests the one variable paper cannot: **you** (the flinch at a real red
number, the 2am urge to override). It is not a graduation or a reward for
the work. The work already paid off the day the machine ran.

## Statistical humility

Even meeting every GO criterion, 30 trades of a fat-tailed strategy carries
a wide error bar. "Pass" means **"not disconfirmed, and consistent with the
backtest"** — not "proven." Size the first real allocation, and your
confidence, accordingly.

## Amendment rule

This document is frozen. It may be revised, but **only** via a visible,
dated, git-committed edit made while **no go/no-go decision is pending**, and
**never** in response to specific results currently in front of you.
Changing the bar to fit the data voids the pre-registration and, with it,
the credibility of every phase that led here.

## Decision record (fill in at the time)

| Date | Closed ETH trades | Expectancy after fees | Drop-best-trade | Beat HODL (risk-adj) | Drawdown survived | Preconditions | Decision |
|------|-------------------|-----------------------|-----------------|----------------------|-------------------|---------------|----------|
|      |                   |                       |                 |                      |                   |               |          |
