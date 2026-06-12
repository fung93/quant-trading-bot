import CandleChart from "@/components/CandleChart";
import HealthStrip from "@/components/HealthStrip";
import Ticker from "@/components/Ticker";
import TimeframeToggle from "@/components/TimeframeToggle";
import { getCandles, getHealth, INTERVAL_MS, type Timeframe } from "@/lib/data";
import { getEthTradesForMarkers } from "@/lib/paper";
import type { SeriesMarker, Time } from "lightweight-charts";

// Always render at request time: this page is a live monitor and must never
// serve a build-time snapshot of the candles table.
export const dynamic = "force-dynamic";

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ tf?: string }>;
}) {
  const timeframe: Timeframe = (await searchParams).tf === "1h" ? "1h" : "1d";

  const [health, btcCandles, ethCandles, ethTrades] = await Promise.all([
    getHealth(),
    getCandles("BTCUSDT", timeframe),
    getCandles("ETHUSDT", timeframe),
    getEthTradesForMarkers().catch(() => []), // pre-migration: no markers
  ]);

  // Entry/exit markers from logged ETH paper trades, snapped to the
  // displayed timeframe's bars (Phase 2 activation of the markers prop).
  const barSec = INTERVAL_MS[timeframe] / 1000;
  const snap = (iso: string) =>
    (Math.floor(new Date(iso).getTime() / 1000 / barSec) * barSec) as Time;
  const ethMarkers: SeriesMarker<Time>[] = [];
  for (const t of ethTrades) {
    if (t.opened_at && t.entry_actual) {
      ethMarkers.push({
        time: snap(t.opened_at), position: "belowBar",
        shape: "arrowUp", color: "#26a69a", text: "E",
      });
    }
    if (t.closed_at && t.exit_actual) {
      ethMarkers.push({
        time: snap(t.closed_at), position: "aboveBar",
        shape: "arrowDown", color: "#ef5350", text: "X",
      });
    }
  }
  ethMarkers.sort((a, b) => (a.time as number) - (b.time as number));

  return (
    <main className="mx-auto w-full max-w-4xl space-y-4 p-4">
      <header className="flex flex-wrap items-baseline justify-between gap-2">
        <h1 className="text-lg font-semibold tracking-tight">quant-bot monitor</h1>
        <Ticker />
      </header>

      <HealthStrip health={health} />

      <TimeframeToggle active={timeframe} />

      <CandleChart symbol="BTCUSDT" timeframe={timeframe} candles={btcCandles} />
      <CandleChart
        symbol="ETHUSDT"
        timeframe={timeframe}
        candles={ethCandles}
        markers={ethMarkers.length ? ethMarkers : undefined}
      />
    </main>
  );
}
