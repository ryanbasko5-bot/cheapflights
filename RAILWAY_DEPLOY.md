# 🚀 Railway Deployment Guide — FareGlitch

## Pre-flight (already done for you)
- [x] `Procfile`, `railway.json`, `nixpacks.toml` point to `prod_start.sh`
- [x] `prod_start.sh` runs Alembic migrations → validates env → starts uvicorn
- [x] `Dockerfile` has health check, non-root user, curl installed
- [x] `.github/workflows/ci.yml` runs tests on push
- [x] Sentry integration wired into FastAPI startup
- [x] Alembic configured with initial migration
- [x] `.env` has real `API_SECRET_KEY` (no more shell expression)
- [x] Placeholder API keys cleaned up

---

## Step 1 — Create Railway project

1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. Click **New Project → Deploy from GitHub repo**.
3. Select **ryanbasko5-bot/cheapflights**.
4. Railway will auto-detect `railway.json` and use Nixpacks.

---

## Step 2 — Add Postgres plugin

1. In your Railway project, click **+ New** → **Database** → **PostgreSQL**.
2. Railway automatically injects `DATABASE_URL` into your service.
3. No config needed on your side — `src/config.py` reads it.

---

## Step 3 — Add Redis plugin (optional, for background jobs)

1. Click **+ New** → **Database** → **Redis**.
2. Railway injects `REDIS_URL`.

---

## Step 4 — Set environment variables

In Railway: click your service → **Variables** tab → **Raw Editor**, paste:

```env
# Required
AMADEUS_API_KEY=<copy from your .env>
AMADEUS_API_SECRET=<copy from your .env>
AMADEUS_ENV=production
API_SECRET_KEY=<copy from your .env>

# Twilio SMS
TWILIO_ACCOUNT_SID=<copy from your .env>
TWILIO_AUTH_TOKEN=<copy from your .env>
TWILIO_PHONE_NUMBER=<copy from your .env>
YOUR_PHONE_NUMBER=<copy from your .env>

# HubSpot
HUBSPOT_API_KEY=<copy from your .env>

# Duffel
DUFFEL_API_TOKEN=<copy from your .env>

# SerpAPI
SERPAPI_KEY=<copy from your .env>

# Feature Flags
ENABLE_AUTO_PUBLISH=false
ENABLE_SMS_ALERTS=true
ENABLE_SLACK_ALERTS=false
DEBUG_MODE=false

# Monitoring (add your Sentry DSN when ready)
# SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
```

> ⚠️ **Do NOT commit real secrets to the repo.** Paste them in Railway Variables only.
> Railway auto-provides `DATABASE_URL` and `REDIS_URL` from plugins — don't set those manually.

---

## Step 5 — Deploy

Railway auto-deploys on push to `main`. Or click **Deploy** manually.

The deploy will:
1. Install dependencies via `pip install -r requirements.txt`
2. Run `bash prod_start.sh` which:
   - Runs `alembic upgrade head` (creates/migrates DB tables)
   - Validates environment variables
   - Starts uvicorn with production settings

---

## Step 6 — Verify

1. Check the deploy logs in Railway for:
   ```
   ✅ Migrations complete
   🌐 Starting uvicorn on port ...
   ```
2. Open your Railway-provided URL (e.g., `https://cheapflights-production.up.railway.app`)
3. Hit the health endpoint: `GET /health` — should return `{"status": "healthy"}`
4. Hit the deals endpoint: `GET /deals/active` — should return `[]` or deal list

---

## Step 7 — Custom domain (optional)

1. In Railway: **Settings** → **Domains** → **Add Custom Domain**
2. Add `api.fareglitch.com` (or your domain)
3. Add the CNAME record Railway gives you to your DNS provider
4. Railway handles HTTPS/SSL automatically

---

## Quick reference

| What | Where |
|------|-------|
| API root | `https://<your-domain>/` |
| Health check | `GET /health` |
| Active deals | `GET /deals/active` |
| Login | `POST /auth/login` |
| Deal unlock | `POST /deals/{number}/unlock` |
| HubSpot webhook | `POST /webhooks/hubspot/payment-success` |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Build fails | Check Railway build logs; ensure `requirements.txt` is valid |
| App crashes on start | Check `Variables` tab — all required env vars set? |
| Database errors | Ensure Postgres plugin is added and `DATABASE_URL` is injected |
| Health check fails | App may still be starting — check deploy logs |
| `settings.X is None` | That env var isn't set in Railway Variables |
