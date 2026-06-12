// Paper-trading reads (anon key, RLS) + shared account constants.
//
// The TypeScript copies of the Python constants live here because the
// dashboard cannot import config/paper_account.py / backtest/config.py.
// Those files are the source of truth - if they change, change this too.
export const INITIAL_CAPITAL_USD = 230; // config/paper_account.py
export const MYR_PER_USD = 4.35; // display only, never accounting
export const KILL_SWITCH_DD = 0.1; // 10% peak-to-trough
export const COST_PER_SIDE = 0.001; // backtest/config.py (0.10%/side measured)

import { getSupabase } from "./supabase";

export interface SignalRow {
  id: number;
  created_at: string;
  symbol: string;
  strategy: string;
  direction: string;
  signal_type: "entry" | "exit";
  bar_open_time: string | null;
  entry_price: number | null;
  stop_loss: number | null;
  size_units: number | null;
  size_usd: number | null;
  reasoning: string | null;
  status: "pending" | "filled" | "cancelled";
  trade_id: number | null;
}

export interface TradeRow {
  id: number;
  signal_id: number | null;
  mode: string;
  opened_at: string | null;
  closed_at: string | null;
  entry_actual: number | null;
  exit_actual: number | null;
  pnl_pct: number | null;
  pnl_usd: number | null;
  outcome: string | null;
  notes: string | null;
  symbol: string | null;
  strategy: string | null;
  stop_loss: number | null;
  size_units: number | null;
  size_usd: number | null;
}

/** Round-trip return after fees - mirror of signal_engine.net_return. */
export function netReturn(entry: number, exit: number): number {
  return (exit / entry) * (1 - COST_PER_SIDE) / (1 + COST_PER_SIDE) - 1;
}

export async function getSignals(limit = 50): Promise<SignalRow[]> {
  const { data, error } = await getSupabase()
    .from("signals")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(limit);
  if (error) throw new Error(`signals query failed: ${error.message}`);
  return (data ?? []) as SignalRow[];
}

export async function getOpenTrades(): Promise<TradeRow[]> {
  const { data, error } = await getSupabase()
    .from("trades")
    .select("*")
    .eq("mode", "paper")
    .eq("outcome", "open")
    .order("opened_at", { ascending: false });
  if (error) throw new Error(`open trades query failed: ${error.message}`);
  return (data ?? []) as TradeRow[];
}

export async function getClosedTrades(symbol?: string): Promise<TradeRow[]> {
  let q = getSupabase()
    .from("trades")
    .select("*")
    .eq("mode", "paper")
    .neq("outcome", "open")
    .order("closed_at", { ascending: true });
  if (symbol) q = q.eq("symbol", symbol);
  const { data, error } = await q;
  if (error) throw new Error(`closed trades query failed: ${error.message}`);
  return (data ?? []) as TradeRow[];
}

export async function getEthTradesForMarkers(): Promise<TradeRow[]> {
  const { data, error } = await getSupabase()
    .from("trades")
    .select("*")
    .eq("mode", "paper")
    .eq("symbol", "ETHUSDT")
    .order("opened_at", { ascending: true });
  if (error) throw new Error(`marker trades query failed: ${error.message}`);
  return (data ?? []) as TradeRow[];
}

export async function getEngineState(): Promise<Record<string, unknown>> {
  const { data, error } = await getSupabase().from("engine_state").select("*");
  if (error) throw new Error(`engine_state query failed: ${error.message}`);
  const out: Record<string, unknown> = {};
  for (const row of data ?? []) out[row.key] = row.value;
  return out;
}

export async function getLatestClose(symbol: string): Promise<number | null> {
  const { data, error } = await getSupabase()
    .from("candles")
    .select("close")
    .eq("symbol", symbol)
    .eq("timeframe", "1h")
    .order("open_time", { ascending: false })
    .limit(1);
  if (error) throw new Error(`latest close query failed: ${error.message}`);
  return data?.[0] ? Number(data[0].close) : null;
}

/** Paper equity: initial + closed ETH PnL + open ETH mark-to-market
 *  (mirror of signal_engine.eth_equity - BTC observational excluded). */
export async function getPaperEquity(): Promise<{
  equity: number;
  closedPnl: number;
  openMtm: number;
}> {
  const closed = await getClosedTrades("ETHUSDT");
  const closedPnl = closed.reduce((s, t) => s + (t.pnl_usd ?? 0), 0);
  let openMtm = 0;
  const open = (await getOpenTrades()).filter((t) => t.symbol === "ETHUSDT");
  if (open.length) {
    const price = await getLatestClose("ETHUSDT");
    const t = open[0];
    if (price && t.entry_actual && t.size_usd) {
      openMtm = t.size_usd * netReturn(t.entry_actual, price);
    }
  }
  return { equity: INITIAL_CAPITAL_USD + closedPnl + openMtm, closedPnl, openMtm };
}

export function fmtMYT(iso: string | null): string {
  if (!iso) return "-";
  return new Date(iso).toLocaleString("en-MY", {
    timeZone: "Asia/Kuala_Lumpur",
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}
