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

## Phase 2 — paper trading (signal engine)

`tsmom_v1` runs every 4h via `.github/workflows/signal-engine.yml` (the job
syncs candles first, then evaluates the last closed 4h bar). ETH is the
primary book — you log fills manually at the dashboard `/log` page. BTC is
observational — the engine auto-fills hypothetical trades at next-bar-open
and they never touch equity or the kill switch.

### One-time setup

1. Run `db/migrations/003_paper_trading.sql` in the Supabase SQL editor.
2. Telegram bot: message **@BotFather** → `/newbot` → name it (e.g.
   `quantbot_signals_bot`) → copy the **token**. Then send any message to
   your new bot, and open
   `https://api.telegram.org/bot<TOKEN>/getUpdates` in a browser — your
   **chat id** is at `result[0].message.chat.id`.
3. GitHub repo secrets (Settings → Secrets → Actions): add
   `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
4. Vercel env vars (server-side, NOT `NEXT_PUBLIC_`): add
   `SUPABASE_SERVICE_ROLE_KEY` and `LOG_PIN` (a 6-digit PIN you choose) —
   these power the PIN-gated `/api/log` write route. Redeploy.

### Position sizing (worked example)

Equity $230, risk 1% = **$2.30**. ETH at $1,650 with ATR(14) = $38 →
stop = 1650 − 2×38 = **$1,574** (distance $76). Units = 2.30 / 76 =
**0.030263 ETH** = **$49.93** (21.7% of equity — under the 95% cap). If ATR
were tiny (say $4 → distance $8), the uncapped size would be ~287% of
equity; the cap clamps it to **$218.50 (95%)**, accepting less than 1%
realized risk rather than leverage. Spot only, always.

### Kill switch

10% peak-to-trough on paper equity halts new entries (exits still
managed) and alerts via Telegram. Manual reset, deliberately — run in the
Supabase SQL editor after you have reviewed the drawdown:

```sql
update engine_state
set value = '{"active": false}'::jsonb, updated_at = now()
where key = 'kill_switch';
```

### Daily rhythm

08:00 MYT heartbeat on Telegram (equity, open positions, engine alive).
Silence at other times means "no signal", never "engine broken" — a broken
run shows red in GitHub Actions and skips the heartbeat.

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
