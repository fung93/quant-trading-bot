"use client";

// Manual fill logging for ETH (Phase 2 Task 3): shows the latest pending
// ETH signal pre-filled with its reference price; the owner adjusts to the
// actual decision price, enters the PIN, submits. Seconds on a phone.

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

  useEffect(() => {
    getSignals(20)
      .then((rows) => {
        const s = rows.find((r) => r.symbol === "ETHUSDT" && r.status === "pending") ?? null;
        setSignal(s);
        if (s?.entry_price) setPrice(String(s.entry_price));
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

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

          <label className="block text-sm">
            <span className="text-gray-400">Actual {signal.signal_type} price (USD)</span>
            <input
              type="number" step="any" required value={price}
              onChange={(e) => setPrice(e.target.value)}
              className="mt-1 w-full rounded-md border border-white/15 bg-black/30 px-3 py-2 font-mono"
            />
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
