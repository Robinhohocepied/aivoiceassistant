# Phase 1 — Foundations & Repo Setup

Status: [~] In Progress · Owner: TBC · Target: TBC

Goals
- Establish repo structure, environment configuration, and baseline logging.
- Provide a health endpoint and basic CI hooks (lint/tests) to validate setup.

Scope In
- Tech stack confirmation, scaffolding, envs, logging, basic docs.

Scope Out
- Business logic for messaging, NLU, calendar.

Tasks
- [x] Confirm stack with stakeholders (FastAPI + OpenAI Agents SDK)
- [x] Define repo layout: `app/`, `agents/`, `connectors/`, `jobs/`, `tests/`
- [x] Add `.env.example` reflecting `docs/plan/CONFIG.md`
- [x] Implement health route (`GET /healthz`) and minimal server
- [x] Configure logging with correlation ID and PII redaction toggle
- [x] Basic CI: lint (e.g., ruff/flake8) and tests (placeholder)
- [x] Document local dev bootstrap steps

Deliverables
- Repo skeleton checked in with README
- Health endpoint responding 200
- `.env.example` and config loader
- Logging configured (level, format, redaction)

Acceptance Criteria
- Service starts locally without errors
- Health route returns 200 in < 100ms
- Lint/test jobs pass in CI

Metrics
- Build success rate; boot time; health route latency

Dependencies
- ADR review/acceptance (stack)

Links
- FRD: `docs/ai_appointment_booking_assistant_functional_requirements_markdown.md`
- Decisions: `docs/plan/DECISIONS.md#adr-0001-tech-stack`
