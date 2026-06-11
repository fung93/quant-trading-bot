import { SYMBOLS, type PairHealth } from "@/lib/data";
import { formatCount, isFresh, relativeAge } from "@/lib/format";
import RefreshButton from "./RefreshButton";

/**
 * Pipeline health, server-rendered on page load. Freshness rule (BUILD_PLAN
 * Phase 0.5): green only if the latest 1h candle for BOTH symbols is less
 * than 2 hours old (measured from candle close - see lib/format.ts).
 */
export default function HealthStrip({ health }: { health: PairHealth[] }) {
  const live = SYMBOLS.every((s) =>
    isFresh(
      health.find((h) => h.symbol === s && h.timeframe === "1h")?.latestOpenTime ?? null,
      "1h"
    )
  );

  return (
    <section className="rounded-lg border border-white/10 bg-white/[0.02] p-3">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span
            className={`h-2.5 w-2.5 rounded-full ${
              live ? "bg-emerald-400" : "bg-red-500"
            }`}
            aria-hidden
          />
          <span className={`text-sm font-medium ${live ? "text-emerald-300" : "text-red-400"}`}>
            {live ? "Pipeline live" : "Pipeline stale"}
          </span>
        </div>
        <RefreshButton />
      </div>

      <dl className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 text-xs sm:grid-cols-4">
        {health.map((h) => (
          <div key={`${h.symbol}-${h.timeframe}`} className="space-y-0.5">
            <dt className="font-mono text-gray-400">
              {h.symbol.replace("USDT", "")} {h.timeframe}
            </dt>
            <dd className="text-gray-200">{relativeAge(h.latestOpenTime)}</dd>
            <dd className="text-gray-500">{formatCount(h.rowCount)} rows</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
