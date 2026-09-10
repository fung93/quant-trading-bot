// Phase 4 gate tracker — mirrors backtest/reports/GO_LIVE_BENCHMARK.md.
//
// It must show the SEVEN frozen criteria, not a friendlier re-derived list:
// building an easier scoreboard beside a frozen bar is how a pre-registration
// gets quietly lowered. NOT YET TESTABLE is never counted as met — a gate that
// was never tested is not a gate that was passed.

export type GateStatus = "MET" | "NOT MET" | "NOT YET TESTABLE";

export interface Gate {
  label: string;
  current: string;
  status: GateStatus;
}

const COLOR: Record<GateStatus, string> = {
  MET: "text-emerald-400",
  "NOT MET": "text-gray-400",
  "NOT YET TESTABLE": "text-amber-400",
};

export default function GateTracker({ gates }: { gates: Gate[] }) {
  const met = gates.filter((g) => g.status === "MET").length;

  return (
    <section className="rounded-lg border border-white/10 bg-white/[0.02] p-3">
      <div className="mb-2 flex items-baseline justify-between">
        <h2 className="text-sm font-medium text-gray-300">Phase 4 gate</h2>
        <span className="font-mono text-sm">
          <span className={met === gates.length ? "text-emerald-400" : "text-gray-200"}>
            {met}
          </span>
          <span className="text-gray-500"> of {gates.length} met</span>
        </span>
      </div>

      <ul className="space-y-1.5 text-xs">
        {gates.map((g) => (
          <li key={g.label} className="flex flex-wrap items-baseline gap-x-2">
            <span className={`font-mono ${COLOR[g.status]}`}>
              {g.status === "MET" ? "✓" : g.status === "NOT YET TESTABLE" ? "–" : "✗"}
            </span>
            <span className="text-gray-300">{g.label}</span>
            <span className="text-gray-500">{g.current}</span>
            {g.status === "NOT YET TESTABLE" && (
              <span className="text-amber-400/70">not yet testable</span>
            )}
          </li>
        ))}
      </ul>

      <p className="mt-3 border-t border-white/5 pt-2 text-[11px] leading-relaxed text-gray-500">
        Mirrors GO_LIVE_BENCHMARK.md, frozen 2026-07-05. Passing all seven makes Phase 4{" "}
        <em>eligible for consideration</em> — never automatic. Criteria marked
        &ldquo;not yet testable&rdquo; are not counted as met.
      </p>
    </section>
  );
}
