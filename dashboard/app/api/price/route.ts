// Live spot price for the /log form.
//
// Server-side on purpose: the browser never talks to Binance directly
// (api.binance.com is ISP-blocked in Malaysia, which is why everything here
// uses data-api.binance.vision), and the base URL stays configurable in one
// place. Read-only, no secrets, no database.

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BASE = process.env.BINANCE_BASE_URL ?? "https://data-api.binance.vision";

export async function GET(req: Request) {
  const symbol = new URL(req.url).searchParams.get("symbol") ?? "ETHUSDT";
  if (!/^[A-Z]{2,12}$/.test(symbol)) {
    return Response.json({ error: "bad symbol" }, { status: 400 });
  }
  try {
    const r = await fetch(`${BASE}/api/v3/ticker/price?symbol=${symbol}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(8000),
    });
    if (!r.ok) {
      return Response.json({ error: `upstream ${r.status}` }, { status: 502 });
    }
    const j = (await r.json()) as { price?: string };
    const price = Number(j.price);
    if (!Number.isFinite(price) || price <= 0) {
      return Response.json({ error: "bad upstream payload" }, { status: 502 });
    }
    return Response.json({ price, at: new Date().toISOString() });
  } catch (e) {
    return Response.json({ error: String(e) }, { status: 502 });
  }
}
