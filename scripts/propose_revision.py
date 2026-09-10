"""The ONLY sanctioned path to a strategy change (Phase 3, Task 3).

Refuses to proceed unless every gate holds, and names the gate that failed.
Passing scaffolds a NEW immutable version file - it never edits an existing
strategy. Even then, the new version must clear the full lab process before
it may replace v1 in the signal engine: paper-trading results never promote
a revision, they only justify testing one.

    python scripts/propose_revision.py --evidence-group ETHUSDT \\
        --justification "..." --new-version tsmom_v2

    python scripts/propose_revision.py --status      # show gate state only
"""

import argparse
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from candle_lib import get_supabase
from review_lib import MIN_TRADES, _dt, group_stats, load_all

STRATEGIES = REPO_ROOT / "strategies"
LEDGER = STRATEGIES / "REVISIONS.md"
MIN_DAYS_BETWEEN = 30
CURRENT = "tsmom_v1"


def last_revision_date():
    """Date of the last ACCEPTED revision, or None if there has never been one."""
    if not LEDGER.exists():
        return None
    latest = None
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("| 20"):
            continue
        stamp = line.split("|")[1].strip()
        try:
            d = datetime.strptime(stamp, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        latest = d if latest is None or d > latest else latest
    return latest


def check_gates(evidence_group, justification, new_version):
    client = get_supabase()
    trades, _signals, _state = load_all(client)
    g = group_stats(trades, evidence_group)
    now = datetime.now(timezone.utc)

    gates = []

    # Gate 1 - evidence volume, in the group the evidence actually came from.
    gates.append({
        "name": f"1. >={MIN_TRADES} closed trades in {evidence_group}",
        "ok": g["n"] >= MIN_TRADES,
        "detail": f"{g['n']} closed {evidence_group} trades "
                  f"(ETH manual and BTC observational are counted separately)",
    })

    # Gate 2 - at most one revision per month.
    last = last_revision_date()
    if last is None:
        gates.append({"name": "2. >=30 days since last accepted revision", "ok": True,
                      "detail": "no prior revision on record"})
    else:
        days = (now - last).days
        gates.append({"name": "2. >=30 days since last accepted revision",
                      "ok": days >= MIN_DAYS_BETWEEN,
                      "detail": f"{days} days since {last.strftime('%Y-%m-%d')}"})

    # Gate 3 - must be a NEW version file, never a mutation.
    target = STRATEGIES / f"{new_version}.py"
    ok3 = new_version != CURRENT and not target.exists()
    gates.append({
        "name": "3. Expressed as a new immutable version",
        "ok": ok3,
        "detail": (f"{new_version}.py would be created"
                   if ok3 else
                   f"{new_version} is the live version or already exists - "
                   "never mutate an existing strategy"),
    })

    # Gate 4 - a written justification naming evidence, not a feeling.
    j = (justification or "").strip()
    ok4 = len(j) >= 40
    gates.append({
        "name": "4. Written justification naming specific evidence",
        "ok": ok4,
        "detail": f"{len(j)} chars" + ("" if ok4 else " - too thin; name the evidence, not a feeling"),
    })

    return gates, g


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence-group", choices=["ETHUSDT", "BTCUSDT"], default="ETHUSDT")
    ap.add_argument("--justification", default="")
    ap.add_argument("--new-version", default="tsmom_v2")
    ap.add_argument("--status", action="store_true", help="report gate state, propose nothing")
    args = ap.parse_args()

    gates, g = check_gates(args.evidence_group, args.justification, args.new_version)

    print("REVISION GATES\n")
    for gate in gates:
        print(f"  [{'PASS' if gate['ok'] else 'BLOCK'}] {gate['name']}")
        print(f"         {gate['detail']}")
    failed = [x for x in gates if not x["ok"]]
    print()

    if args.status:
        print(f"status only - {len(gates) - len(failed)}/{len(gates)} gates pass")
        return

    if failed:
        print(f"REFUSED. {len(failed)} gate(s) block this revision:")
        for gate in failed:
            print(f"  - {gate['name']}: {gate['detail']}")
        print("\nNo files were written. This refusal is the point: it stops a change")
        print("being made on noise, on a feeling, or on too little evidence.")
        sys.exit(1)

    # All gates pass - scaffold the new version from v1, never editing v1.
    src = STRATEGIES / f"{CURRENT}.py"
    dst = STRATEGIES / f"{args.new_version}.py"
    shutil.copyfile(src, dst)
    header = (
        f'"""{args.new_version} - REVISION SCAFFOLD, created '
        f'{datetime.now(timezone.utc).strftime("%Y-%m-%d")}.\n\n'
        f"Justification recorded at proposal time:\n{args.justification}\n\n"
        f"Evidence group: {args.evidence_group} ({g['n']} closed trades, "
        f"expectancy {g['expectancy']:+.2f}%/trade).\n\n"
        f"NOT YET ELIGIBLE FOR LIVE USE. This file must clear the full lab process\n"
        f"before it may replace {CURRENT} in the signal engine:\n"
        f"  1. parameters frozen BEFORE any run\n"
        f"  2. train on 2021-2023, validation run ONCE\n"
        f"  3. robustness grid, training window only\n"
        f"  4. verdict document + EXPERIMENT_LEDGER.md row\n"
        f'Paper-trading results justify TESTING a revision; they never promote one.\n"""\n\n'
    )
    body = dst.read_text(encoding="utf-8")
    body = body[body.index('"""', body.index('"""') + 3) + 3:].lstrip("\n")
    dst.write_text(header + body, encoding="utf-8")

    if not LEDGER.exists():
        LEDGER.write_text(
            "# Accepted strategy revisions\n\n"
            "One row per accepted revision. Gates enforced by "
            "scripts/propose_revision.py.\n\n"
            "| date | from | to | evidence group | trades | justification |\n"
            "|---|---|---|---|---|---|\n", encoding="utf-8")
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(f"| {datetime.now(timezone.utc).strftime('%Y-%m-%d')} | {CURRENT} | "
                 f"{args.new_version} | {args.evidence_group} | {g['n']} | "
                 f"{args.justification[:120]} |\n")

    print(f"ALL GATES PASSED. Scaffolded strategies/{args.new_version}.py from {CURRENT}.")
    print(f"Logged in strategies/REVISIONS.md\n")
    print("REQUIRED NEXT STEP - the new version is NOT live and must not be used until it")
    print("clears the same lab process every earlier version faced:")
    print("  train 2021-2023 -> validation ONCE -> robustness grid -> verdict + ledger row")
    print("Only after a passing verdict may the signal engine point at it.")


if __name__ == "__main__":
    main()
