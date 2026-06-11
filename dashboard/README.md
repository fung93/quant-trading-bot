# quant-bot dashboard (Phase 0.5 — monitor page)

Single-page monitor for the candle pipeline: BTC/ETH candlestick charts
(1h/1d), a data-health strip with a pipeline live/stale indicator, and a
cosmetic live spot ticker. Reads Supabase with the **anon key only** (RLS
read-only policy on `candles`).

## Run locally

```bash
cd dashboard
cp .env.example .env.local   # fill in the two values (Supabase -> Project Settings -> API keys -> anon public)
npm install
npm run dev                  # http://localhost:3000
```

The service role key is never used here. Only the anon ("public") key.

## Deploy to Vercel

1. [vercel.com/new](https://vercel.com/new) → Import the `quant-trading-bot` GitHub repo.
2. **Root Directory: click Edit and set it to `dashboard`** — this is the one
   setting that matters. It scopes deploys so Python-only commits don't
   trigger builds. Framework preset auto-detects Next.js; leave build
   settings default.
3. Environment Variables — add both, for Production (and Preview if you
   like):
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`  ← anon public key, **not** service role
4. Deploy. The page URL is public; it exposes only what the anon key can
   read (candles), which is public market data anyway.

## Verify RLS (do this once after first deploy)

The anon key ships in the public JS bundle, so prove the database denies it
everything except candle reads. Replace `<URL>` and `<ANON>`:

```bash
# 1. candles readable -> expect one row of JSON
curl -s "<URL>/rest/v1/candles?select=symbol,open_time&limit=1" \
  -H "apikey: <ANON>" -H "Authorization: Bearer <ANON>"

# 2. other tables NOT readable -> expect [] (RLS filters every row)
curl -s "<URL>/rest/v1/signals?select=*"    -H "apikey: <ANON>" -H "Authorization: Bearer <ANON>"
curl -s "<URL>/rest/v1/trades?select=*"     -H "apikey: <ANON>" -H "Authorization: Bearer <ANON>"
curl -s "<URL>/rest/v1/strategies?select=*" -H "apikey: <ANON>" -H "Authorization: Bearer <ANON>"

# 3. candles NOT writable -> expect a row-level security violation error
curl -s -X POST "<URL>/rest/v1/candles" \
  -H "apikey: <ANON>" -H "Authorization: Bearer <ANON>" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"HACKUSDT","timeframe":"1h","open_time":"2020-01-01T00:00:00Z"}'
```

Because `signals`/`trades`/`strategies` are empty in Phase 0.5, `[]` alone
can't distinguish "denied" from "empty". For a strict test: insert one dummy
row with the service role key, confirm the anon query still returns `[]`,
then delete the dummy row.

## Notes

- Spot ticker fetches `data-api.binance.vision` from the browser — Binance's
  official public market-data host. Not `api.binance.com`, which is
  ISP-blocked in Malaysia. The ticker hides itself if the fetch fails.
- Charts render in the browser's local timezone.
- Phase 1 will overlay backtest entry/exit markers on the charts; the chart
  component already accepts a (currently unused) `markers` prop for this.
