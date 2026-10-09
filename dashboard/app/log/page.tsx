"use client";

// Manual fill logging for ETH (Phase 2 Task 3).
//
// The price field starts EMPTY and must stay that way. It used to pre-fill
// with the signal's reference price, so submitting without editing recorded a
// perfect 0.000% slippage - and that is exactly what happened on every fill
// the owner logged (trades 2, 10 and 16, all reading 0.000%). The slippage
// metric that review_lib calls "Phase 3's most valuable output" was measuring
// nothing: the form was answering its own question.
//
// Reference and live price are shown as read-only context so the number typed
// is a decision, not a default. Do not reintroduce a pre-filled value or a
// one-tap autofill button.

import { useEffect, useState } from "react";
import { fmtMYT, getSignals, type SignalRow } from "@/lib/paper";

export default function LogPage() {
  const [signal, setSignal] = useState<SignalRow | null>(null);
  const [loading, setLoading] = useState(true);
  const [price, setPrice] = useState("");
  const [pin, setPin] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [live, setLive] = useState<number | null>(null);
  const [liveAt, setLiveAt] = useState<string | null>(null);

  useEffect(() => {
    getSignals(20)
      .then((rows) => {
        // Deliberately NOT setting price here - see the note at the top.
        setSignal(rows.find((r) => r.symbol === "ETHUSDT" && r.status === "pending") ?? null);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  // Live spot, refreshed while the form is open, as context for the typed price.
  useEffect(() => {
    if (!signal) return;
    let alive = true;
    const pull = async () => {
      try {
        const r = await fetch(`/api/price?symbol=${signal.symbol}`, { cache: "no-store" });
        const j = await r.json();
        if (alive && r.ok && typeof j.price === "number") {
          setLive(j.price);
          setLiveAt(new Date(j.at).toLocaleTimeString());
        }
      } catch {
        /* context only - never block logging on a price fetch */
      }
    };
    pull();
    const id = setInterval(pull, 15_000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, [signal]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!signal) return;
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ signalId: signal.id, price: Number(price), pin }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error ?? `HTTP ${res.status}`);
      setResult(
        json.kind === "entry"
          ? `Entry logged - trade #${json.tradeId} open.`
          : `Exit logged - ${json.outcome}, ${json.pnlPct > 0 ? "+" : ""}${json.pnlPct}% ($${json.pnlUsd}).`
      );
      setSignal(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-md space-y-4 p-4">
      <h1 className="text-lg font-semibold tracking-tight">Log a fill</h1>

      {loading && <p className="text-sm text-gray-400">Loading latest signal…</p>}

      {!loading && result && (
        <div className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 p-3 text-sm text-emerald-300">
          {result}
        </div>
      )}

      {!loading && !result && !signal && (
        <p className="rounded-lg border border-white/10 bg-white/[0.02] p-3 text-sm text-gray-400">
          Nothing awaiting a log - no pending ETH signal.
        </p>
      )}

      {signal && (
        <form onSubmit={submit} className="space-y-3 rounded-lg border border-white/10 bg-white/[0.02] p-4">
          <div className="text-sm">
            <span className={`mr-2 rounded px-1.5 py-0.5 font-mono text-xs ${
              signal.signal_type === "entry" ? "bg-emerald-500/20 text-emerald-300" : "bg-red-500/20 text-red-300"
            }`}>
              {signal.signal_type.toUpperCase()}
            </span>
            <span className="font-mono">{signal.symbol}</span>
            <span className="ml-2 text-gray-500">{fmtMYT(signal.bar_open_time)}</span>
          </div>

          <p className="whitespace-pre-wrap text-xs leading-relaxed text-gray-400">
            {signal.reasoning}
          </p>

          <div className="grid grid-cols-2 gap-2 rounded-md border border-white/10 bg-black/20 p-2 text-xs">
            <div>
              <div className="text-gray-500">Signal reference</div>
              <div className="font-mono text-gray-300">
                {signal.entry_price ?? "-"}
              </div>
            </div>
            <div>
              <div className="text-gray-500">Live now</div>
              <div className="font-mono text-gray-300">
                {live !== null ? live.toFixed(2) : "…"}
                {live !== null && signal.entry_price && (
                  <span className="ml-1 text-gray-500">
                    ({((live / Number(signal.entry_price) - 1) * 100).toFixed(2)}%)
                  </span>
                )}
              </div>
              {liveAt && <div className="text-[10px] text-gray-600">{liveAt}</div>}
            </div>
          </div>

          <label className="block text-sm">
            <span className="text-gray-400">Actual {signal.signal_type} price (USD)</span>
            <input
              type="number" step="any" required value={price} placeholder="type the price you see"
              onChange={(e) => setPrice(e.target.value)}
              className="mt-1 w-full rounded-md border border-white/15 bg-black/30 px-3 py-2 font-mono"
            />
            <span className="mt-1 block text-[11px] leading-relaxed text-gray-500">
              Deliberately blank. The two numbers above are context, not an answer -
              type what you could actually transact at, so slippage measures something.
            </span>
          </label>

          <label className="block text-sm">
            <span className="text-gray-400">PIN</span>
            <input
              type="password" inputMode="numeric" pattern="[0-9]*" maxLength={6} required value={pin}
              onChange={(e) => setPin(e.target.value)}
              className="mt-1 w-full rounded-md border border-white/15 bg-black/30 px-3 py-2 font-mono tracking-widest"
            />
          </label>

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            type="submit" disabled={busy}
            className="w-full rounded-md bg-white/15 px-4 py-2 text-sm font-medium hover:bg-white/25 disabled:opacity-50"
          >
            {busy ? "Logging…" : `Log ${signal.signal_type}`}
          </button>
        </form>
      )}
    </main>
  );
}
