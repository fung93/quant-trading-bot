---
name: binance-api-blocked-malaysia
description: api.binance.com is ISP-blocked on this machine (Malaysia); use data-api.binance.vision for public market data
metadata: 
  node_type: memory
  type: project
  originSessionId: e1d05667-10a8-42ea-abaa-60b5c89e4195
---

`api.binance.com` and `api1.binance.com` time out from this machine (Malaysian ISP block, verified 2026-06-10; google.com fine), while `data-api.binance.vision` — Binance's official public market-data host with identical `/api/v3/klines` and `/api/v3/time` — returns 200.

**Why:** any local script hitting api.binance.com will hang for its full timeout and fail; GitHub Actions runners are unaffected.

**How to apply:** default all Binance market-data calls to `https://data-api.binance.vision`. In quant-bot this is already the default in `scripts/candle_lib.py`, overridable via `BINANCE_BASE_URL` env var. Related: [[quant-bot-phase-0-state]].
