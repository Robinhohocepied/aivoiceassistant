# WhatsApp Cloud API Setup (Phase 2)

Endpoints
- Verification + Inbound: `GET/POST {BASE_URL}/webhooks/whatsapp`
  - Verify query params (GET): `hub.mode`, `hub.verify_token`, `hub.challenge`
  - Inbound (POST): raw JSON from WhatsApp (Cloud API)

Environment
- `WHATSAPP_TOKEN`: Cloud API access token
- `WHATSAPP_VERIFY_TOKEN`: Webhook verify token (you define it in Meta UI)
- `WHATSAPP_PHONE_ID`: Sender phone number ID
- `WHATSAPP_BASE_URL`: API base URL (default `https://graph.facebook.com/v18.0`)

Local verification
- Start: `uvicorn app.main:app --reload --port 8080`
- Verify: `curl "http://localhost:8080/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=${WHATSAPP_VERIFY_TOKEN}&hub.challenge=12345"`
- Expected: `12345` echoed if token matches.

Inbound payload
- The app normalizes messages to a lightweight structure and stores them in-memory (Phase 2); see `connectors/whatsapp/types.py`.

Outbound send wrapper
- `connectors/whatsapp/client.py` exposes `WhatsAppClient.send_text(to, body)` with simple retries.
- If env is not configured, `from_settings(settings)` returns `None`.

Outbound quick test (Graph API)
- Direct send to verify token/phone pairing:
```
make qa-send TO=15551234567
```
- Requires: `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID` in your env or `.env`.
- If you get 401 Unauthorized: token expired/wrong app or not authorized for this phone ID.
- If you get 400 invalid parameter: use digits-only recipient, ensure your number is added as Tester in Dev mode.

Notes
- Use HTTPS and a public callback URL in Meta App → Webhooks.
- For sandbox testing, configure your phone number and verify delivery.
- Phase 3 will pass inbound messages to the OpenAI Agents SDK and generate replies.
