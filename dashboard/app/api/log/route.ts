// PIN-gated write path for manual ETH fill logging (Phase 2 Task 3).
//
// The browser keeps using the anon key (read-only). This route runs ONLY on
// the server and uses SUPABASE_SERVICE_ROLE_KEY from a server-side Vercel
// env var (never NEXT_PUBLIC_). A 6-digit PIN (LOG_PIN env var) gates every
// write. Rate limiting is per serverless instance (naive by design - the
// PIN is the real gate; this just slows brute force).

import { createClient } from "@supabase/supabase-js";
import {
  COST_PER_SIDE,
  INITIAL_CAPITAL_USD,
  MAX_POSITION_PCT,
  RISK_PER_TRADE,
} from "@/lib/paper";

export const runtime = "nodejs";

const attempts = new Map<string, { count: number; first: number }>();
const WINDOW_MS = 10 * 60 * 1000;
const MAX_ATTEMPTS = 8;

function rateLimited(ip: string): boolean {
  const now = Date.now();
  const a = attempts.get(ip);
  if (!a || now - a.first > WINDOW_MS) {
    attempts.set(ip, { count: 1, first: now });
    return false;
  }
  a.count += 1;
  return a.count > MAX_ATTEMPTS;
}

function netReturn(entry: number, exit: number): number {
  // After-fees round trip - keep in sync with backtest/config.py (0.10%/side).
  return (exit / entry) * (1 - COST_PER_SIDE) / (1 + COST_PER_SIDE) - 1;
}

export async function POST(req: Request) {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";
  if (rateLimited(ip)) {
    return Response.json({ error: "Too many attempts - wait 10 minutes." }, { status: 429 });
  }

  let body: { signalId?: number; price?: number; pin?: string };
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: "Bad request" }, { status: 400 });
  }
  const { signalId, price, pin } = body;
  if (!signalId || !price || !pin || !(price > 0)) {
    return Response.json({ error: "signalId, price and pin are required" }, { status: 400 });
  }

  const expected = process.env.LOG_PIN;
  if (!expected) {
    return Response.json({ error: "LOG_PIN not configured on the server" }, { status: 500 });
  }
  if (pin !== expected) {
    await new Promise((r) => setTimeout(r, 1000)); // slow wrong guesses
    return Response.json({ error: "Wrong PIN" }, { status: 401 });
  }

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const serviceKey = process.env.SUPABASE_SERVICE_ROLE_KEY; // server-side only
  if (!url || !serviceKey) {
    return Response.json({ error: "Server missing Supabase credentials" }, { status: 500 });
  }
  const db = createClient(url, serviceKey, { auth: { persistSession: false } });

  const { data: sigRows, error: sigErr } = await db
    .from("signals").select("*").eq("id", signalId).limit(1);
  if (sigErr || !sigRows?.length) {
    return Response.json({ error: "Signal not found" }, { status: 404 });
  }
  const sig = sigRows[0];
  if (sig.symbol !== "ETHUSDT") {
    return Response.json({ error: "Only ETH fills are logged manually" }, { status: 400 });
  }
  if (sig.status !== "pending") {
    return Response.json({ error: `Signal already ${sig.status}` }, { status: 409 });
  }

  const now = new Date().toISOString();

  if (sig.signal_type === "entry") {
    // Size from the price ACTUALLY filled, never from the signal's unit count.
    //
    // The rule is "risk 1% of equity"; the unit count is derived from it using
    // the signal-bar price. Inheriting those units after a late fill breaks
    // the rule silently: on 2026-10-10 a signal arrived 18.7h late, the fill
    // was +1.33% above the reference with the stop unchanged, and the
    // signal's units would have risked $4.24 = 1.48% of equity against a
    // $2.87 budget. The kill switch assumes every trade risks 1%.
    const stop = Number(sig.stop_loss);
    if (!(stop > 0) || price <= stop) {
      return Response.json(
        { error: `Fill ${price} is at or below the stop ${stop} - the trade is already invalid. Check the price.` },
        { status: 400 }
      );
    }

    // Equity for sizing: starting capital plus realized ETH P&L. There is
    // never an open ETH position at entry time (one position at a time).
    const { data: closedRows } = await db
      .from("trades").select("pnl_usd")
      .eq("symbol", "ETHUSDT").eq("mode", "paper").not("closed_at", "is", null);
    const equity =
      INITIAL_CAPITAL_USD +
      (closedRows ?? []).reduce((a, r) => a + Number(r.pnl_usd ?? 0), 0);

    let units = (equity * RISK_PER_TRADE) / (price - stop);
    const cap = (equity * MAX_POSITION_PCT) / price;
    const capped = units > cap;
    if (capped) units = cap;
    const sizeUsd = units * price;

    const { data: trade, error } = await db.from("trades").insert({
      signal_id: sig.id,
      mode: "paper",
      notes: capped ? "manual fill; size capped at 95% of equity" : "manual fill",
      symbol: sig.symbol,
      strategy: sig.strategy,
      opened_at: now,
      entry_actual: price,
      stop_loss: stop,
      size_units: units,
      size_usd: sizeUsd,
      outcome: "open",
    }).select().single();
    if (error) return Response.json({ error: error.message }, { status: 500 });

    await db.from("signals").update({ status: "filled", trade_id: trade.id }).eq("id", sig.id);
    return Response.json({ ok: true, kind: "entry", tradeId: trade.id });
  }

  // Exit signal: close the referenced trade.
  if (!sig.trade_id) {
    return Response.json({ error: "Exit signal has no linked trade" }, { status: 409 });
  }
  const { data: tRows, error: tErr } = await db
    .from("trades").select("*").eq("id", sig.trade_id).limit(1);
  if (tErr || !tRows?.length || tRows[0].outcome !== "open") {
    return Response.json({ error: "Linked trade missing or already closed" }, { status: 409 });
  }
  const trade = tRows[0];
  const pnlPct = netReturn(Number(trade.entry_actual), price);
  const pnlUsd = Number(trade.size_usd) * pnlPct;
  const outcome = Math.abs(pnlPct) < 1e-4 ? "breakeven" : pnlPct > 0 ? "win" : "loss";

  const { error: updErr } = await db.from("trades").update({
    closed_at: now,
    exit_actual: price,
    pnl_pct: pnlPct,
    pnl_usd: pnlUsd,
    outcome,
  }).eq("id", trade.id);
  if (updErr) return Response.json({ error: updErr.message }, { status: 500 });

  await db.from("signals").update({ status: "filled" }).eq("id", sig.id);
  return Response.json({
    ok: true, kind: "exit", outcome,
    pnlPct: +(pnlPct * 100).toFixed(3), pnlUsd: +pnlUsd.toFixed(2),
  });
}
