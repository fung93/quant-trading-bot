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

// ---- Phase 4 gate computation (mirrors GO_LIVE_BENCHMARK.md, frozen) ----
import type { Gate } from "@/components/GateTracker";
import { getCandles } from "./data";

export const MIN_TRADES = 30;
export const EXPECTANCY_BAR = 0.5; // percent per trade, after fees

export async function computeGates(): Promise<Gate[]> {
  const closed = await getClosedTrades("ETHUSDT");
  const open = (await getOpenTrades()).filter((t) => t.symbol === "ETHUSDT");
  const pcts = closed.map((t) => (t.pnl_pct ?? 0) * 100);
  const n = pcts.length;
  const expectancy = n ? pcts.reduce((a, b) => a + b, 0) / n : NaN;

  // drop the single largest winner
  let dropBest = NaN;
  if (n >= 2) {
    const sorted = [...pcts].sort((a, b) => a - b).slice(0, -1);
    dropBest = sorted.reduce((a, b) => a + b, 0) / sorted.length;
  }

  const { equity } = await getPaperEquity();
  const price = await getLatestClose("ETHUSDT");
  const all = [...closed, ...open];
  const firstEntry = all.length
    ? all.slice().sort((a, b) => (a.opened_at ?? "").localeCompare(b.opened_at ?? ""))[0]
        .entry_actual
    : null;
  const startMs = all.length
    ? Math.min(...all.map((t) => new Date(t.opened_at ?? Date.now()).getTime()))
    : Date.now();
  const days = Math.floor((Date.now() - startMs) / 86400000);
  const hodlReturn = price && firstEntry ? (price / firstEntry - 1) * 100 : NaN;
  const stratReturn = (equity / INITIAL_CAPITAL_USD - 1) * 100;

  // HODL max drawdown over the live window, from daily closes.
  const daily = await getCandles("ETHUSDT", "1d", 400);
  const inWindow = daily.filter((c) => c.time * 1000 >= startMs).map((c) => c.close);
  let runMax = -Infinity;
  let hodlMaxDd = 0; // percent, <= 0
  for (const px of inWindow) {
    runMax = Math.max(runMax, px);
    hodlMaxDd = Math.min(hodlMaxDd, (px / runMax - 1) * 100);
  }
  const decline20 = hodlMaxDd <= -20;
  const state = await getEngineState();
  const peak = Math.max(
    Number((state["equity_peak"] as { peak?: number })?.peak ?? INITIAL_CAPITAL_USD),
    equity
  );
  const stratDd = peak > 0 ? ((peak - equity) / peak) * 100 : 0;

  const pendingEth = (await getSignals(100)).filter(
    (s) => s.symbol === "ETHUSDT" && s.status === "pending"
  ).length;

  const testable = n >= MIN_TRADES;
  const fmt = (x: number) => (Number.isFinite(x) ? `${x >= 0 ? "+" : ""}${x.toFixed(2)}%` : "n/a");

  return [
    {
      label: "≥30 closed ETH trades",
      current: `${n}/30`,
      status: n >= MIN_TRADES ? "MET" : "NOT MET",
    },
    {
      label: "≥3 months + ≥20% ETH drawdown survived",
      current: `${days}d elapsed, worst ETH DD ${hodlMaxDd.toFixed(1)}%`,
      status: days >= 91 && decline20 ? "MET" : decline20 ? "NOT MET" : "NOT YET TESTABLE",
    },
    {
      label: `expectancy ≥ +${EXPECTANCY_BAR}%/trade`,
      current: `${fmt(expectancy)} (n=${n})`,
      status: testable ? (expectancy >= EXPECTANCY_BAR ? "MET" : "NOT MET") : "NOT YET TESTABLE",
    },
    {
      label: "drop-best-trade still ≥ 0",
      current: fmt(dropBest),
      status: testable ? (dropBest >= 0 ? "MET" : "NOT MET") : "NOT YET TESTABLE",
    },
    {
      label: "beat buy-and-hold (return)",
      current: `${fmt(stratReturn)} vs HODL ${fmt(hodlReturn)}`,
      status: stratReturn >= hodlReturn ? "MET" : "NOT MET",
    },
    {
      // Defined "over that decline" (the ≥20% decline of criterion 2).
      // Never counted as met before one has occurred.
      label: "equity DD smaller than HODL's through the ≥20% decline",
      current: decline20
        ? `strategy ${stratDd.toFixed(1)}% vs HODL ${Math.abs(hodlMaxDd).toFixed(1)}%`
        : `no ≥20% decline yet (worst ${hodlMaxDd.toFixed(1)}%)`,
      status: !decline20 ? "NOT YET TESTABLE" : stratDd < Math.abs(hodlMaxDd) ? "MET" : "NOT MET",
    },
    {
      label: "execution integrity (all fills logged)",
      current: `${pendingEth} unlogged`,
      status: pendingEth === 0 ? "MET" : "NOT MET",
    },
  ];
}
