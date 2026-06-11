import { getSupabase } from "./supabase";

export const SYMBOLS = ["BTCUSDT", "ETHUSDT"] as const;
export const TIMEFRAMES = ["1h", "1d"] as const;

export type MarketSymbol = (typeof SYMBOLS)[number];
export type Timeframe = (typeof TIMEFRAMES)[number];

export const INTERVAL_MS: Record<Timeframe, number> = {
  "1h": 3_600_000,
  "1d": 86_400_000,
};

export interface Candle {
  /** Candle open time as UNIX seconds (UTC). */
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PairHealth {
  symbol: MarketSymbol;
  timeframe: Timeframe;
  /** ISO timestamptz of the newest candle, or null when the table is empty. */
  latestOpenTime: string | null;
  rowCount: number;
}

interface CandleRow {
  open_time: string;
  open: number | string;
  high: number | string;
  low: number | string;
  close: number | string;
  volume: number | string;
}

/**
 * Most recent `limit` candles for one symbol/timeframe, oldest-first
 * (lightweight-charts requires ascending time order).
 */
export async function getCandles(
  symbol: MarketSymbol,
  timeframe: Timeframe,
  limit = 500
): Promise<Candle[]> {
  const { data, error } = await getSupabase()
    .from("candles")
    .select("open_time, open, high, low, close, volume")
    .eq("symbol", symbol)
    .eq("timeframe", timeframe)
    .order("open_time", { ascending: false })
    .limit(limit);

  if (error) {
    throw new Error(`candles query failed for ${symbol} ${timeframe}: ${error.message}`);
  }

  return ((data ?? []) as CandleRow[])
    .map((r) => ({
      time: Math.floor(new Date(r.open_time).getTime() / 1000),
      open: Number(r.open),
      high: Number(r.high),
      low: Number(r.low),
      close: Number(r.close),
      volume: Number(r.volume),
    }))
    .reverse();
}

/**
 * Latest open_time and exact row count for every symbol x timeframe.
 * One request per pair: the count rides along on the latest-row query
 * (`count: "exact"` reports the full filtered count despite `limit(1)`),
 * so nothing close to a full table is ever fetched.
 */
export async function getHealth(): Promise<PairHealth[]> {
  return Promise.all(
    SYMBOLS.flatMap((symbol) =>
      TIMEFRAMES.map(async (timeframe): Promise<PairHealth> => {
        const { data, count, error } = await getSupabase()
          .from("candles")
          .select("open_time", { count: "exact" })
          .eq("symbol", symbol)
          .eq("timeframe", timeframe)
          .order("open_time", { ascending: false })
          .limit(1);

        if (error) {
          throw new Error(`health query failed for ${symbol} ${timeframe}: ${error.message}`);
        }

        return {
          symbol,
          timeframe,
          latestOpenTime: (data?.[0] as { open_time: string } | undefined)?.open_time ?? null,
          rowCount: count ?? 0,
        };
      })
    )
  );
}
