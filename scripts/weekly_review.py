"""Phase 3 weekly review - READ ONLY. Never changes strategy state.

Writes reviews/YYYY-Www.md, prints it, and pushes a condensed version to
Telegram. Handles a zero-activity week honestly rather than crashing.

    python scripts/weekly_review.py [--days 7] [--no-telegram]
"""

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from candle_lib import get_supabase
from signal_engine import PRIMARY, OBSERVATIONAL, tg_send
from config.paper_account import INITIAL_CAPITAL_USD, KILL_SWITCH_DD
from review_lib import (
    EXP, EXPECTED_TRADES_PER_MONTH, MIN_TRADES, _dt, drop_best_test, equity_now,
    eth_slippage, group_stats, hodl_compare, load_all, myt, percentile_bands,
    streak_context, unlogged_eth_signals,
)

REVIEWS = REPO_ROOT / "reviews"


def pct(x, nd=2):
    return "n/a" if x != x else f"{x:+.{nd}f}%"


def build(days=7):
    c = get_supabase()
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)
    trades, signals, state = load_all(c)

    eq, eth_realized, mtm, price = equity_now(c, trades)
    eth = group_stats(trades, PRIMARY)
    btc = group_stats(trades, OBSERVATIONAL)
    hodl = hodl_compare(trades, price)
    slips = eth_slippage(trades, signals)
    unlogged = unlogged_eth_signals(signals)

    peak_state = float(state.get("equity_peak", {}).get("value", {}).get("peak", INITIAL_CAPITAL_USD))
    peak = max(peak_state, eq)
    dd = (peak - eq) / peak * 100 if peak else 0.0
    kill = state.get("kill_switch", {}).get("value", {}).get("active", False)

    L = []
    A = L.append
    A(f"# Weekly review - {myt(now.isoformat(), '%Y-%m-%d')} (week {now.isocalendar()[1]})")
    A("")
    A(f"Window: last {days} days. Paper trading only - no real capital. "
      "This report reads; it never decides.")
    A("")

    # ---------------- 1. week's activity ----------------
    A("## 1. This week")
    A("")
    wk_sig = [s for s in signals if _dt(s["created_at"]) >= since]
    wk_closed = [t for t in trades if t.get("closed_at") and _dt(t["closed_at"]) >= since]
    wk_opened = [t for t in trades if t.get("opened_at") and _dt(t["opened_at"]) >= since]
    if not wk_sig and not wk_closed and not wk_opened:
        A("Nothing happened. No signals, no fills, no exits. For a strategy that")
        A("trades ~2.8 times a month per asset, a quiet week is the normal case,")
        A("not a fault.")
    else:
        A(f"- signals issued: {len(wk_sig)} "
          f"(ETH {len([s for s in wk_sig if s['symbol'] == PRIMARY])}, "
          f"BTC {len([s for s in wk_sig if s['symbol'] == OBSERVATIONAL])})")
        A(f"- trades opened: {len(wk_opened)} | closed: {len(wk_closed)}")
        for t in wk_closed:
            hold = (_dt(t["closed_at"]) - _dt(t["opened_at"])).days
            A(f"  - [#{t['id']}] {t['symbol']} {t['entry_actual']} -> {t['exit_actual']} "
              f"= {float(t['pnl_pct']) * 100:+.2f}% (${float(t['pnl_usd']):+.2f}), held {hold}d")
    A("")
    if unlogged:
        A(f"> **{len(unlogged)} UNLOGGED ETH signal(s)** - a process failure. "
          "Unlogged signals silently corrupt the sample.")
        for s in unlogged:
            A(f"> - [{s['id']}] {s['signal_type']} ref {s['entry_price']} "
              f"bar {myt(s['bar_open_time'])}")
        A("")
    else:
        A("No unlogged ETH signals.")
        A("")

    # ---------------- 2. groups, never mixed ----------------
    A("## 2. Running totals (groups never mixed)")
    A("")
    A("| group | closed | win rate | avg win | avg loss | expectancy/trade | realized $ |")
    A("|---|---|---|---|---|---|---|")
    for g, label in ((eth, "ETH manual"), (btc, "BTC observational")):
        flag = " (weak)" if g["weak"] else ""
        A(f"| {label} | {g['n']}{flag} | {pct(g['win_rate'], 1)} | {pct(g['avg_win'])} | "
          f"{pct(g['avg_loss'])} | **{pct(g['expectancy'])}** | ${g['realized_usd']:+.2f} |")
    A("")
    A(f"Statistics from fewer than {MIN_TRADES} trades are flagged weak - same standard "
      "as the lab. BTC is a calibration control, not part of the verdict.")
    A("")
    A(f"Equity **${eq:.2f}** (realized ${eth_realized:+.2f}, open MTM ${mtm:+.2f}) | "
      f"peak ${peak:.2f} | drawdown {dd:.1f}% of the {KILL_SWITCH_DD * 100:.0f}% kill line | "
      f"kill switch: {'ACTIVE' if kill else 'off'}")
    A("")

    # ---------------- 3. expectancy in context ----------------
    A("## 3. Expectancy in context")
    A("")
    if eth["n"] >= 1:
        b = percentile_bands(PRIMARY, eth["n"])
        inside = b[5] <= eth["expectancy"] <= b[95]
        A(f"ETH realized **{pct(eth['expectancy'])}**/trade over {eth['n']} trade(s).")
        A("")
        A(f"If the strategy performed exactly as backtested, {eth['n']} trade(s) would land:")
        A("")
        A("| percentile | 5th | 25th | 50th | 75th | 95th |")
        A("|---|---|---|---|---|---|")
        A(f"| expectancy | {b[5]:+.2f}% | {b[25]:+.2f}% | {b[50]:+.2f}% | "
          f"{b[75]:+.2f}% | {b[95]:+.2f}% |")
        A("")
        A(f"-> realized figure is **{'INSIDE' if inside else 'OUTSIDE'}** the normal range. "
          "A number without its band invites panic; this is the band.")
    else:
        A("No closed ETH trades yet - expectancy is not measurable.")
    A("")

    # ---------------- 4. streaks ----------------
    A("## 4. Losing streaks (reported factually)")
    A("")
    st = streak_context(eth["pcts"], PRIMARY)
    A(f"- current losing streak: **{st['current']}**")
    A(f"- longest so far: **{st['longest']}**")
    if st["prob_at_least_this_long"] == st["prob_at_least_this_long"]:
        A(f"- probability of a streak this long or longer at {eth['n']} trades: "
          f"**{st['prob_at_least_this_long']:.0f}%**")
    A("")
    A("Context: ~22 of every 30 trades are expected to lose, and a run of 8 consecutive "
      "losses has ~52% probability across 30 trades. Streaks are the cost of a "
      "26%-win-rate strategy, not evidence against it.")
    A("")

    # ---------------- 5. divergence ----------------
    A("## 5. Divergence from Phase 1d expectations")
    A("")
    A("| metric | expected | realized | note |")
    A("|---|---|---|---|")
    for g, label in ((eth, "ETH"), (btc, "BTC")):
        e = EXP[g["symbol"]]["expectancy"]
        A(f"| {label} expectancy/trade | {e:+.2f}% | {pct(g['expectancy'])} | "
          f"{'weak sample' if g['weak'] else 'meaningful'} |")
    if hodl:
        months = max(hodl["days"] / 30.44, 0.01)
        realized_rate = (eth["n"] + btc["n"]) / months
        A(f"| trade frequency (combined) | {EXPECTED_TRADES_PER_MONTH:.1f}/mo | "
          f"{realized_rate:.1f}/mo | over {hodl['days']}d |")
    A("")

    A("### Execution gap (slippage) - the measured model-vs-human cost")
    A("")
    if not slips:
        A("No logged ETH fills yet - slippage unavailable.")
    else:
        A("| trade | type | signal ref | actual fill | slippage | adverse | logged after bar close |")
        A("|---|---|---|---|---|---|---|")
        for r in slips:
            late = f"{r['lateness_h']:.1f}h" if r["lateness_h"] is not None else "-"
            A(f"| #{r['trade_id']} | {r['type']} | {r['ref']:.2f} | {r['actual']:.2f} | "
              f"{r['slip_pct']:+.3f}% | {r['adverse_pct']:+.3f}% | {late} |")
        adv = sum(r["adverse_pct"] for r in slips) / len(slips)
        lates = [r["lateness_h"] for r in slips if r["lateness_h"] is not None]
        A("")
        A(f"**Mean adverse slippage: {adv:+.3f}% per fill** over {len(slips)} fill(s). "
          "This is the real gap between the model and your execution, and it feeds "
          "Phase 4 planning directly.")
        if lates:
            A("")
            A(f"Mean logging lateness: **{sum(lates) / len(lates):.1f}h**. Lateness is a "
              "separate risk from slippage: in August a 2-day delay dropped two entry "
              "signals entirely, which no slippage figure would reveal.")
    A("")

    # ---------------- 6. gate tracker: the frozen seven ----------------
    A("## 6. Phase 4 gate status - mirrors GO_LIVE_BENCHMARK.md")
    A("")
    met = 0
    rows = []

    c1 = eth["n"] >= MIN_TRADES
    rows.append(("1. >=30 closed ETH trades", f"{eth['n']}/30", "MET" if c1 else "NOT MET"))
    met += c1

    if hodl:
        months_ok = hodl["days"] >= 91
        dd20 = hodl["eth_price_dd"] <= -20
        c2 = months_ok and dd20
        status2 = "MET" if c2 else ("NOT YET TESTABLE" if not dd20 else "NOT MET")
        rows.append(("2. >=3 months AND >=20% ETH drawdown survived",
                     f"{hodl['days']}d, worst ETH DD {hodl['eth_price_dd']:.1f}%", status2))
        met += c2
    else:
        rows.append(("2. >=3 months AND >=20% ETH drawdown", "no data", "NOT MET"))

    c3 = (eth["n"] >= MIN_TRADES and eth["expectancy"] == eth["expectancy"]
          and eth["expectancy"] >= 0.5)
    rows.append(("3. Expectancy >= +0.5%/trade after fees",
                 f"{pct(eth['expectancy'])} (n={eth['n']})",
                 "MET" if c3 else ("NOT YET TESTABLE" if eth["n"] < MIN_TRADES else "NOT MET")))
    met += c3

    db = drop_best_test(eth["pcts"])
    c4 = eth["n"] >= MIN_TRADES and db is not None and db >= 0
    rows.append(("4. Drop-best-trade still >= 0",
                 pct(db) if db is not None else "n/a",
                 "MET" if c4 else ("NOT YET TESTABLE" if eth["n"] < MIN_TRADES else "NOT MET")))
    met += c4

    if hodl:
        strat_ret = (eq / INITIAL_CAPITAL_USD - 1) * 100
        c5 = strat_ret >= hodl["hodl_return"]
        rows.append(("5. Beat buy-and-hold (return)",
                     f"strategy {strat_ret:+.1f}% vs HODL {hodl['hodl_return']:+.1f}%",
                     "MET" if c5 else "NOT MET"))
        met += c5
        # Criterion 6 is defined "over that decline" - the >=20% ETH decline of
        # criterion 2. Until one has occurred it is NOT YET TESTABLE and is never
        # counted as met (an earlier version wrongly scored it against a -6.5%
        # wobble, inflating the count).
        if not dd20:
            rows.append(("6. Equity DD smaller than HODL's through the >=20% decline",
                         f"no >=20% decline yet (worst {hodl['eth_price_dd']:.1f}%)",
                         "NOT YET TESTABLE"))
        else:
            c6 = dd < abs(hodl["hodl_max_dd"])
            rows.append(("6. Equity DD smaller than HODL's through the >=20% decline",
                         f"strategy {dd:.1f}% vs HODL {abs(hodl['hodl_max_dd']):.1f}%",
                         "MET" if c6 else "NOT MET"))
            met += c6

    c7 = len(unlogged) == 0
    rows.append(("7. Execution integrity (all fills logged)",
                 f"{len(unlogged)} unlogged", "MET" if c7 else "NOT MET"))
    met += c7

    A("| criterion | current | status |")
    A("|---|---|---|")
    for r in rows:
        A(f"| {r[0]} | {r[1]} | {r[2]} |")
    A("")
    A(f"### **{met} of 7 conditions met**")
    A("")
    A("Passing all seven makes Phase 4 *eligible for consideration* - never automatic. "
      "Criteria marked NOT YET TESTABLE are not counted as met: a gate that was never "
      "tested is not a gate that was passed.")
    A("")
    A(f"Kill switch: {'ACTIVE' if kill else 'never triggered'} | equity drawdown "
      f"{dd:.1f}% vs {KILL_SWITCH_DD * 100:.0f}% paper kill line")
    A("")

    # ---------------- 7. engine health ----------------
    A("## 7. Engine health")
    A("")
    lat = []
    for s in signals:
        if s.get("bar_open_time") and s.get("created_at"):
            bc = _dt(s["bar_open_time"]) + timedelta(hours=4)
            lat.append((_dt(s["created_at"]) - bc).total_seconds() / 60)
    if lat:
        recent = ", ".join(f"{x:.0f}m" for x in lat[-5:])
        A(f"- signal latency (bar close to written): last 5 = {recent} | "
          f"all-time median {sorted(lat)[len(lat) // 2]:.0f}m")
    ev = state.get("last_evaluated_bar_ETHUSDT", {}).get("updated_at")
    A(f"- last engine evaluation: {myt(ev)} MYT" if ev else "- last engine evaluation: unknown")
    A(f"- last heartbeat: {state.get('last_heartbeat_date', {}).get('value', {}).get('date', 'unknown')}")
    A("")

    # ---------------- 8. rules ----------------
    A("## 8. Process rules (in force)")
    A("")
    A("- No strategy parameter change more than once per month.")
    A(f"- **No change based on fewer than {MIN_TRADES} closed trades.**")
    A("- Every change is a new version file (tsmom_v1 -> tsmom_v2), never a mutation.")
    A("- GO_LIVE_BENCHMARK.md may not be edited while a verdict is pending.")
    A("- Changes may only be proposed through scripts/propose_revision.py.")
    A("")
    permitted = eth["n"] >= MIN_TRADES
    A(f"### Decisions permitted this week: **{'YES - gates open' if permitted else 'NONE'}**")
    if not permitted:
        A("")
        A(f"Fewer than {MIN_TRADES} closed ETH trades ({eth['n']}). No strategy change may "
          "be made or proposed on this evidence. The correct action this week is to keep "
          "logging faithfully and wait.")
    A("")

    return "\n".join(L), {
        "met": met, "eth_n": eth["n"], "equity": eq, "dd": dd,
        "unlogged": len(unlogged), "expectancy": eth["expectancy"],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--no-telegram", action="store_true")
    args = ap.parse_args()

    report, summary = build(args.days)
    print(report)

    now = datetime.now(timezone.utc)
    REVIEWS.mkdir(exist_ok=True)
    path = REVIEWS / f"{now.isocalendar()[0]}-W{now.isocalendar()[1]:02d}.md"
    path.write_text(report, encoding="utf-8")
    print(f"\nsaved: reviews/{path.name}")

    if not args.no_telegram:
        exp = ("n/a" if summary["expectancy"] != summary["expectancy"]
               else f"{summary['expectancy']:+.2f}%")
        tg_send(
            f"Weekly review - {now.strftime('%Y-%m-%d')}\n"
            f"ETH closed {summary['eth_n']}/30 | expectancy {exp}\n"
            f"equity ${summary['equity']:.2f} | drawdown {summary['dd']:.1f}%\n"
            f"unlogged signals: {summary['unlogged']}\n"
            f"Phase 4 gate: {summary['met']} of 7 met\n"
            f"Decisions permitted: {'YES' if summary['eth_n'] >= 30 else 'NONE (<30 trades)'}"
        )


if __name__ == "__main__":
    main()
