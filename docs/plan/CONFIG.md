# Configuration & Environment

Environment variables (example names) and configuration required by phases.

Core
- `APP_ENV` — environment name (`dev`, `stage`, `prod`)
- `CLINIC_TZ` — default timezone (e.g., `Europe/Brussels`)
- `DEFAULT_LOCALE` — default locale (e.g., `fr-FR`)

OpenAI / Agents SDK
- `OPENAI_API_KEY` — API key for model access
- `AGENT_MODEL` — model name (e.g., `gpt-4.1`)
 - `AGENT_AUTO_REPLY` — `true` to auto-reply via WhatsApp using agent output (default `false`)
 - `AGENT_DRY_RUN` — `true` to avoid live sends when auto-replying (default `true`)

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
- Demo / WebChat
  - `DEMO_DAILY_LIMIT` (default: 20) – max new demo sessions per day
  - `DEMO_TIMEZONE` (default: Europe/Amsterdam) – timezone to derive the daily date key
  - `DEMO_SESSION_TTL_HOURS` (default: 48) – demo session retention window
  - `MAX_MESSAGES_PER_DEMO_SESSION` (default: 40) – abuse protection per session

- Calendar per channel
  - `CALENDAR_ID_WHATSAPP` – production calendar ID (optional; falls back to `GOOGLE_CALENDAR_ID`)
  - `CALENDAR_ID_WEB_DEMO` – dedicated demo calendar ID
