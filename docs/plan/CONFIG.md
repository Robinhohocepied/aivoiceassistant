# Configuration & Environment

Environment variables (example names) and configuration required by phases.

Core
- `APP_ENV` — environment name (`dev`, `stage`, `prod`)
- `CLINIC_TZ` — default timezone (e.g., `Europe/Brussels`)
- `DEFAULT_LOCALE` — default locale (e.g., `fr-FR`)

OpenAI / Agents SDK
- `OPENAI_API_KEY` — API key for model access
- `AGENT_MODEL` — model name (e.g., `gpt-4.1`)

WhatsApp (Cloud API)
- `WHATSAPP_TOKEN` — access token
- `WHATSAPP_VERIFY_TOKEN` — webhook verify token
- `WHATSAPP_PHONE_ID` — sender phone ID
- `WHATSAPP_BASE_URL` — API base URL

Google Calendar
- `GOOGLE_CREDS_JSON` — base64-encoded service account JSON or file path
- `GOOGLE_CALENDAR_ID` — clinic calendar identifier

Scheduling / Jobs
- `REMINDER_HOURS_BEFORE` — default `24`

Security & Privacy
- `REDACT_LOGS` — `true` to mask PII in logs
- `DATA_RETENTION_DAYS` — e.g., `90`

Webhook / Server
- `PORT` — service port (e.g., `8080`)
- `BASE_URL` — public base URL (for webhooks)

Notes
- Do not commit real secrets.
- For local dev, use a `.env` file loaded via a standard library (e.g., `python-dotenv`).
- Production should use a secrets manager (e.g., cloud provider).

