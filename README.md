# Mediflow — AI Appointment Booking Assistant

This repository contains an incremental implementation of an AI-driven appointment booking assistant. Work is organized by phases under `docs/plan/` and is grounded in the functional requirements in `docs/ai_appointment_booking_assistant_functional_requirements_markdown.md`.

Quick start
- One command run (creates venv, installs deps, runs): `make start`
  - Optionally choose Python: `make PYTHON=python3.11 start`
- Health check: `curl -i http://localhost:8080/healthz`

Structure
- `app/` — FastAPI app, config, logging utilities
- `agents/` — orchestration and conversation logic (future phases)
- `connectors/` — external integrations (WhatsApp, Google Calendar)
- `jobs/` — background jobs (reminders, cleanup)
- `tests/` — unit tests

Phase 1 deliverables
- Health endpoint `GET /healthz` returning service status and build info.
- Structured JSON logging with correlation IDs and optional PII redaction.
- `.env.example` and config loader.
- Linting (ruff) and unit test skeleton.
- Agents SDK readiness: environment variables for OpenAI + optional client stub (`agents/client.py`).

Local development
- Create venv: `make venv`
- Install deps: `make install`
- Run: `make run` (defaults to `PORT=8080`)
- Test: `make test`
- Lint: `make lint` (if ruff installed in venv)

WhatsApp (Phase 2)
- Webhook: `GET/POST /webhooks/whatsapp`
  - Verify (GET): responds with `hub.challenge` when `hub.verify_token` matches `WHATSAPP_VERIFY_TOKEN`.
  - Inbound (POST): accepts Cloud API JSON; messages normalized and stored in-memory; forwarded to Agents hook (stub).
- Outbound: use `connectors/whatsapp/client.py` (`WhatsAppClient.send_text`).
- Setup guides:
  - WhatsApp: `docs/plan/SETUP_WHATSAPP.md`
  - Local ngrok (webhooks over HTTPS): `docs/plan/SETUP_NGROK.md`
