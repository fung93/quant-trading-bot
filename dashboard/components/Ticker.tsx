"use client";

import { useEffect, useState } from "react";

// Binance's official public market-data host. Deliberately NOT
// api.binance.com: that domain is ISP-blocked in Malaysia, where this page
// is mostly viewed. data-api.binance.vision serves the same /api/v3
// endpoints and answers browsers with Access-Control-Allow-Origin: *.
const TICKER_URL =
  "https://data-api.binance.vision/api/v3/ticker/price?symbols=" +
  encodeURIComponent('["BTCUSDT","ETHUSDT"]');

const REFRESH_MS = 15_000;

interface Prices {
  BTCUSDT?: number;
  ETHUSDT?: number;
}

/**
 * Cosmetic live spot ticker, independent of the database. Hides itself on
 * fetch failure (network/region block) instead of erroring the page, and
 * keeps retrying quietly in the background.
 */
export default function Ticker() {
  const [prices, setPrices] = useState<Prices | null>(null);
  const [updatedAt, setUpdatedAt] = useState<string>("");

  useEffect(() => {
    let cancelled = false;

    async function tick() {
      try {
        const res = await fetch(TICKER_URL, { signal: AbortSignal.timeout(8_000) });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const rows: { symbol: string; price: string }[] = await res.json();
        if (cancelled) return;
        const next: Prices = {};
        for (const r of rows) {
          if (r.symbol === "BTCUSDT") next.BTCUSDT = Number(r.price);
          if (r.symbol === "ETHUSDT") next.ETHUSDT = Number(r.price);
        }
        setPrices(next);
        setUpdatedAt(new Date().toLocaleTimeString());
      } catch {
        if (!cancelled) setPrices(null); // hide gracefully; retry next tick
      }
    }

    tick();
    const id = setInterval(tick, REFRESH_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  if (!prices?.BTCUSDT || !prices?.ETHUSDT) return null;

  const fmt = (n: number) =>
    n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  return (
    <p className="font-mono text-xs text-gray-400">
      BTC <span className="text-gray-200">${fmt(prices.BTCUSDT)}</span>
      <span className="mx-2 text-gray-600">·</span>
      ETH <span className="text-gray-200">${fmt(prices.ETHUSDT)}</span>
      <span className="ml-2 text-gray-600">{updatedAt}</span>
    </p>
  );
}
