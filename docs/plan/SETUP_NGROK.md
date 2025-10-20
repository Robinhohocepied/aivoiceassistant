# Local ngrok Setup for WhatsApp Webhooks

This guide shows how to expose your local FastAPI server to Meta (WhatsApp Cloud API) using ngrok so you can receive real webhook events while developing locally.

## Prerequisites
- App runs locally on `:8080` (default): `make start`
- `.env` contains `WHATSAPP_VERIFY_TOKEN` (used by webhook verification)
- A WhatsApp Business Account (WABA) with a Phone Number ID (Cloud API)
- ngrok installed and authenticated

## 1) Install and authenticate ngrok
- macOS: `brew install ngrok`
- Add your auth token (from dashboard): `ngrok config add-authtoken <YOUR_TOKEN>`

## 2) Start your API locally
- `make start`
  - Creates a virtualenv, installs dependencies, and starts FastAPI on `http://localhost:8080`.
- Health check (local): `curl -i http://localhost:8080/healthz`

## 3) Expose the server via ngrok
- Start tunnel (foreground): `make tunnel`
  - Or directly: `ngrok http 8080`
- Find the public HTTPS URL:
  - `make tunnel-url` → prints something like `https://abcd1234.ngrok.io`

## 4) Configure the webhook in Meta (Facebook Developers)
1. Open developers.facebook.com → Your App → WhatsApp → Configuration
2. Set Webhook
   - Callback URL: `https://<your-ngrok-domain>/webhooks/whatsapp`
   - Verify Token: the same value as `WHATSAPP_VERIFY_TOKEN` in your `.env`
3. Click Verify/Save (should return 200 and echo the challenge)
4. Subscribe to events
   - App → Webhooks
   - Subscribe to object `whatsapp_business_account`
   - Enable the `messages` field
   - Ensure the correct Business Account (WABA) is selected

## 5) Quick verification from your terminal
- With the tunnel running:
```
make qa-verify TUNNEL=https://<your-ngrok-domain>
```
- Or explicit curl:
```
curl -i "https://<your-ngrok-domain>/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=$WHATSAPP_VERIFY_TOKEN&hub.challenge=12345"
```
Expected: `200 OK` and the response body `12345`.

## 6) Manual QA – receiving a real message
- From your personal WhatsApp, send a message to your Business number.
- Watch your app logs:
  - You should see JSON lines like `"logger":"connectors.whatsapp.webhook","msg":"whatsapp_inbound"` and fields `from`, `type`, `text`.
- Optional: use the dev-only debug endpoint in a browser:
  - `GET https://<your-ngrok-domain>/webhooks/whatsapp/_debug/messages`
  - Returns the normalized messages received during this run.

## 7) Optional – send a dry-run outbound message
This builds the payload without hitting the network.
```
source .venv/bin/activate
python - <<'PY'
from app.config import load_settings
from connectors.whatsapp.client import from_settings
s = load_settings(); c = from_settings(s)
assert c, "WhatsApp client not configured (set WHATSAPP_TOKEN and WHATSAPP_PHONE_ID)"
import asyncio
print(asyncio.run(c.send_text(to="<RECIPIENT_WA_ID>", body="Hello from Mediflow!", dry_run=True)))
PY
```

## Makefile shortcuts
- `make start` — create venv, install deps, run API (:8080)
- `make tunnel` — start ngrok tunnel to :8080 (foreground)
- `make tunnel-url` — print current ngrok HTTPS URL
- `make qa-verify [TUNNEL=…]` — verify webhook via tunnel
- `make qa-inbound [TUNNEL=…]` — send a sample inbound payload via tunnel
- You can override `PORT` for the app/tunnel: `make PORT=9000 start` and `make PORT=9000 tunnel`

## Troubleshooting
- 404 at `/` in ngrok: expected. Use `/healthz` and `/webhooks/whatsapp` paths.
- 403 on verify: `WHATSAPP_VERIFY_TOKEN` mismatch; ensure Meta uses the same value as your `.env`.
- No “Recent Deliveries” in Meta:
  - Confirm the Callback URL is saved to the correct app
  - Confirm you subscribed `whatsapp_business_account` to `messages`
  - Ensure the WABA/phone number is linked to this app
  - Ensure the ngrok URL is current (it changes each run)
- Dev vs Live: In Dev mode, only app admins/developers/testers can interact. For broader testing, switch to Live and complete compliance steps.
- Not seeing message text in logs: set `REDACT_LOGS=false` in `.env` for local QA.
- SSL/HTTPS: Meta requires HTTPS. Always use the `https://` ngrok URL.

---
For end-to-end WhatsApp setup details, also see `docs/plan/SETUP_WHATSAPP.md`.

