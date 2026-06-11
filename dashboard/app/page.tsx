import CandleChart from "@/components/CandleChart";
import HealthStrip from "@/components/HealthStrip";
import Ticker from "@/components/Ticker";
import TimeframeToggle from "@/components/TimeframeToggle";
import { getCandles, getHealth, type Timeframe } from "@/lib/data";

// Always render at request time: this page is a live monitor and must never
// serve a build-time snapshot of the candles table.
export const dynamic = "force-dynamic";

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ tf?: string }>;
}) {
  const timeframe: Timeframe = (await searchParams).tf === "1h" ? "1h" : "1d";

  const [health, btcCandles, ethCandles] = await Promise.all([
    getHealth(),
    getCandles("BTCUSDT", timeframe),
    getCandles("ETHUSDT", timeframe),
  ]);

  return (
    <main className="mx-auto w-full max-w-4xl space-y-4 p-4">
      <header className="flex flex-wrap items-baseline justify-between gap-2">
        <h1 className="text-lg font-semibold tracking-tight">quant-bot monitor</h1>
        <Ticker />
      </header>

      <HealthStrip health={health} />

      <TimeframeToggle active={timeframe} />

      <CandleChart symbol="BTCUSDT" timeframe={timeframe} candles={btcCandles} />
      <CandleChart symbol="ETHUSDT" timeframe={timeframe} candles={ethCandles} />
    </main>
  );
}
