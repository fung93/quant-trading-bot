import { INTERVAL_MS, type Timeframe } from "./data";

/** "38 min ago" style age of an ISO timestamp. */
export function relativeAge(iso: string | null): string {
  if (!iso) return "no data";
  const min = Math.floor((Date.now() - new Date(iso).getTime()) / 60_000);
  if (min < 1) return "just now";
  if (min < 60) return `${min} min ago`;
  const h = Math.floor(min / 60);
  if (h < 48) return `${h} h ago`;
  return `${Math.floor(h / 24)} d ago`;
}

/**
 * Pipeline freshness for one pair. Age is measured from the candle's CLOSE
 * (open_time + interval), not its open: the newest closed 1h candle is
 * always 1-2 h past its open even when the pipeline is perfectly healthy,
 * so an open-time rule would flash red in the tail minutes of every hour.
 */
export function isFresh(
  latestOpenTime: string | null,
  timeframe: Timeframe,
  maxAgeMs = 2 * 3_600_000
): boolean {
  if (!latestOpenTime) return false;
  const closedAt = new Date(latestOpenTime).getTime() + INTERVAL_MS[timeframe];
  return Date.now() - closedAt < maxAgeMs;
}

export function formatCount(n: number): string {
  return n.toLocaleString("en-US");
}
