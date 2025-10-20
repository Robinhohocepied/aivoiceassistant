# OpenAI Setup (Local)

Use this guide to connect the app to OpenAI for Phase 3 (Conversation & NLU).

## 1) Create an API Key
- Go to platform.openai.com → API keys
- Create a key and keep it secret

## 2) Configure environment
- Add these to your `.env` (see `.env.example`):
```
OPENAI_API_KEY=sk-...
AGENT_MODEL=gpt-4.1        # or gpt-4o-mini for lower cost
# Optional (advanced):
OPENAI_BASE_URL=           # custom endpoint (e.g., proxy/self-host)
OPENAI_ORG_ID=             # org header if applicable
OPENAI_PROJECT=            # project context (optional)
```
- Restart the app (`make start`) so the config reloads
- Health check shows `agents_configured: true` when the key is present

## 3) Sanity test the connection
- Run: `make agent-test`
- Expected: prints a short model response in your terminal

## 4) Enable auto-replies (optional)
- In `.env`:
```
AGENT_AUTO_REPLY=true
AGENT_DRY_RUN=true   # change to false to send real WhatsApp messages
```
- Requires WhatsApp credentials (`WHATSAPP_TOKEN`, `WHATSAPP_PHONE_ID`).
- When enabled, the agent will extract fields and send a French follow-up/confirmation.

## 5) Choosing a model
- `gpt-4.1`: good general reasoning; use for higher quality
- `gpt-4o-mini`: cost/perf optimized; good default for early prototyping
- You can change the model anytime via `AGENT_MODEL`

## 6) Where the client is created
- Code: `agents/client.py` → `create_agents_client(settings)`
- Uses environment from `app/config.py` and avoids network calls until used

## 7) Troubleshooting
- `agents_configured` is false: missing/invalid `OPENAI_API_KEY`
- Network errors: check firewall/VPN; if needed, set `OPENAI_BASE_URL` to your proxy
- Rate limits: reduce test frequency; prefer `gpt-4o-mini` for iteration
- 401/403: re-check the key, org/project settings

Next steps
- Implement session state keyed by phone number
- Add prompts/guardrails in French to extract name, reason, preferred time
- Wire agent calls into `agents/ingest.py` and optionally auto-reply via WhatsApp client
