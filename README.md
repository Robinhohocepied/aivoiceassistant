# Mediflow — AI Appointment Booking Assistant

This repository contains an incremental implementation of an AI-driven appointment booking assistant. Work is organized by phases under `docs/plan/` and is grounded in the functional requirements in `docs/ai_appointment_booking_assistant_functional_requirements_markdown.md`.

Quick start
- Create a `.env` from `.env.example` and set values as needed.
- Install dependencies (Python 3.11+ recommended):
  - With `uv`: `uv pip install -r requirements.txt` (or use `pyproject.toml` with `uv pip install -r <(uv pip compile pyproject.toml)`)
  - With `pip`: `pip install -r requirements.txt` (or `pip install -e .` if using `pyproject.toml`)
- Run the API: `uvicorn app.main:app --reload --port 8080`
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
- Lint: `ruff check .`
- Test: `pytest -q`
- Run: `uvicorn app.main:app --reload --port 8080`

WhatsApp (Phase 2)
- Webhook: `GET/POST /webhooks/whatsapp`
  - Verify (GET): responds with `hub.challenge` when `hub.verify_token` matches `WHATSAPP_VERIFY_TOKEN`.
  - Inbound (POST): accepts Cloud API JSON; messages normalized and stored in-memory; forwarded to Agents hook (stub).
- Outbound: use `connectors/whatsapp/client.py` (`WhatsAppClient.send_text`).
- Setup guide: `docs/plan/SETUP_WHATSAPP.md`

