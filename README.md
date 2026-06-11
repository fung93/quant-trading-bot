# quant-bot

Personal quantitative trading system for BTC/ETH. Read [BUILD_PLAN.md](BUILD_PLAN.md)
for the full plan. **Current phase: 0 — Data Foundation** (candle data flowing
into Supabase hourly, with full historical backfill from 2021-01-01).

Everything runs on free tiers: Binance public market data (no API key),
Supabase free tier, GitHub Actions cron.

## Setup

### 1. Run the database migrations

In the Supabase SQL editor (the dedicated quant-bot project), paste and run,
in order:

1. `db/migrations/001_candles.sql` — candles table, index, RLS with anon read
2. `db/migrations/002_registry.sql` — strategies/signals/trades, RLS deny-by-default

### 2. Configure credentials

Local: copy `.env.example` to `.env` and fill in both values from
Supabase → Project Settings → API. `.env` is gitignored; the service role key
must never be committed or exposed to a client.

GitHub Actions (**required before the hourly sync can run**): in the repo,
Settings → Secrets and variables → Actions → New repository secret, add:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

### 3. Install dependencies

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows; on WSL2/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the backfill locally

```bash
python scripts/backfill.py
```

Pulls 1h and 1d candles for BTCUSDT and ETHUSDT from 2021-01-01 to now
(~50,000 rows per symbol on 1h). Takes a few minutes. Idempotent and
resumable: if interrupted, re-run it — it continues from the newest stored
candle and never duplicates rows.

### 5. Enable the hourly sync

The workflow `.github/workflows/sync-candles.yml` runs at 7 and 37 minutes
past each hour (two slots, because GitHub occasionally drops scheduled runs
under load — whichever slot fires self-heals any backlog) once the repo is
pushed to GitHub and the secrets from step 2 are set.
Trigger it once manually (Actions → sync-candles → Run workflow) to confirm
it's green.

## Verifying the data

```bash
python scripts/verify.py
```

Prints, per symbol/timeframe: row count, earliest/latest candle, and any gaps
(missing candles between consecutive rows). Each gap includes the exact
`backfill.py` command to re-fetch that range. Binance has rare legitimate
gaps from exchange maintenance — if a re-fetch returns nothing, the gap is on
Binance's side and is fine to leave.

## Notes

- Market data comes from `data-api.binance.vision` — Binance's official
  public market-data host (same `/api/v3/klines`, no API key). This is the
  default instead of `api.binance.com` because the latter is ISP-blocked in
  Malaysia, where the backfill runs locally. Override with `BINANCE_BASE_URL`
  if ever needed.
- Only **closed** candles are ever written. Both scripts drop any candle
  whose close time is still in the future (checked against Binance server
  time), so partially-formed candles never enter the table.
- All scripts are safe to re-run at any time; writes are idempotent upserts
  keyed on `(symbol, timeframe, open_time)`.
