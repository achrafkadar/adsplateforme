# Wenov Ads Platform (Meta App Review)

Minimal public web app for Meta App Review demos — landing, login, dashboard, and privacy policy.

**Not** the full agency ADS PLATEFORM codebase.

## Local run

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ADMIN_EMAIL=review@wenov.ca
export ADMIN_PASSWORD='your-secure-password'
export SESSION_SECRET='long-random-string'
uvicorn main:app --reload --port 8000
```

Open http://127.0.0.1:8000

## Environment variables

| Variable | Purpose |
|----------|---------|
| `ADMIN_EMAIL` | Login email for review / demo |
| `ADMIN_PASSWORD` | Login password |
| `SESSION_SECRET` | Signed session cookie secret |

## Deploy on Render

### Option A — Blueprint (`render.yaml`)

1. In Render Dashboard → **New** → **Blueprint**
2. Connect `achrafkadar/adsplateforme`
3. Apply the Blueprint; set `ADMIN_PASSWORD` (and confirm `ADMIN_EMAIL`) in Environment
4. After deploy, open the `*.onrender.com` URL

### Option B — Web Service (manual)

1. **New** → **Web Service** → repo `achrafkadar/adsplateforme`
2. Runtime: **Python 3**
3. Build: `pip install -r requirements.txt`
4. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add env vars: `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `SESSION_SECRET`
6. Deploy

### Custom domain `ads.wenov.ca`

1. Render → your service → **Settings** → **Custom Domains** → add `ads.wenov.ca`
2. At your DNS provider, create a **CNAME** record:
   - Host: `ads`
   - Target: `adsplateforme.onrender.com` (use the exact hostname Render shows)
3. Wait for TLS certificate provisioning in Render

## Routes

- `/` — public landing
- `/login` — sign in
- `/dashboard` — post-login overview (Serenity / clients / messaging placeholder)
- `/privacy` — privacy policy (Meta App Review)
- `/health` — health check

## Privacy URL for Meta

`https://<your-render-host>/privacy` or `https://ads.wenov.ca/privacy` after DNS.
