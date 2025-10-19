# Decisions (ADR Log)

Use this log to record architectural decisions. Status may be Proposed, Accepted, or Superseded.

ADR-0001: Tech Stack
- Status: Accepted
- Context: FRD suggests using an orchestration framework (OpenAI Agent Builder or OpenAI Agents SDK).
- Decision: Use Python FastAPI for the service and OpenAI Agents SDK for conversation orchestration and guardrails.
- Consequences: Python ecosystem for connectors and scheduling; clear async model. Conversation logic implemented via OpenAI Agents SDK with tool/function definitions for WhatsApp messaging, calendar, and utilities. Prompts and guardrails localized (FR).

ADR-0002: Messaging Provider
- Status: Proposed
- Context: FRD specifies WhatsApp Business API.
- Decision: Use WhatsApp Cloud API (Meta) with webhook verification and sandbox testing.
- Consequences: Requires Meta app configuration, tokens, and webhook hosting with HTTPS.

ADR-0003: Calendar Provider
- Status: Proposed
- Context: FRD specifies Google Calendar.
- Decision: Use Google Calendar API with a service account (or OAuth if patient invites require personal calendars).
- Consequences: Manage service account credentials securely; event sharing and ICS fallback.

ADR-0004: Locale & Timezone
- Status: Proposed
- Context: FRD targets French-speaking patients in Europe/Brussels.
- Decision: Default locale FR (fr-FR) with timezone Europe/Brussels.
- Consequences: Localized formatting and FR date parsing throughout.

ADR-0005: Data Retention & Minimization
- Status: Proposed
- Context: GDPR compliance with deletion within 24 hours upon request.
- Decision: Store minimal PII; set retention window (e.g., 90 days configurable). Implement deletion workflow.
- Consequences: Requires redaction/masking and deletion jobs; logs must avoid sensitive content.

ADR-0006: Job Scheduling
- Status: Proposed
- Context: Need for T-24h reminders and cleanup tasks.
- Decision: Use APScheduler for prototype; can migrate to managed scheduler in production.
- Consequences: In-process scheduler dependency; consider idempotency and persistence.
