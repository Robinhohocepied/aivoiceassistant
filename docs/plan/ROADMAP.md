# Roadmap

This roadmap outlines the phase-by-phase plan and links to detailed trackers for each phase.

Status Legend: [ ] Not started · [~] In progress · [x] Done

- [x] Phase 1 — Foundations & Repo Setup (`docs/plan/phases/phase-01-foundations.md`)
  - Goals: repo structure, envs, health endpoint, logging baseline.
- [~] Phase 2 — WhatsApp Messaging Integration (`docs/plan/phases/phase-02-whatsapp-integration.md`)
  - Goals: webhook verify/receive, reply flow, send wrapper, traceability.
- [~] Phase 3 — French Conversation Flow & NLU (`docs/plan/phases/phase-03-conversation-nlu.md`)
  - Goals: capture name/reason/time; French prompts/guardrails; session state.
- [ ] Phase 4 — Calendar Integration & Scheduling (`docs/plan/phases/phase-04-calendar-scheduling.md`)
  - Goals: Google Calendar, availability lookup, FR date parsing, event creation.
- [ ] Phase 5 — Confirmations & Reminders (`docs/plan/phases/phase-05-confirmations-reminders.md`)
  - Goals: booking summary, ICS fallback, T-24h reminder, FR localization.
- [ ] Phase 6 — Rescheduling & Cancellation (`docs/plan/phases/phase-06-reschedule-cancel.md`)
  - Goals: keywords detection, change flow, audit trail.
- [ ] Phase 7 — Emergency Handling & Handoff (`docs/plan/phases/phase-07-emergency-handoff.md`)
  - Goals: detect URGENT, alert staff, pause/resume automation.
- [ ] Phase 8 — Privacy, Security & GDPR (`docs/plan/phases/phase-08-privacy-gdpr.md`)
  - Goals: consent, data minimization, PII masking, delete flow.
- [ ] Phase 9 — Logging, Monitoring & Analytics (`docs/plan/phases/phase-09-logging-monitoring.md`)
  - Goals: structured logs, correlation IDs, metrics, alerts.
- [ ] Phase 10 — Performance & Reliability (`docs/plan/phases/phase-10-performance-reliability.md`)
  - Goals: ≤5s response, retries/backoff, idempotency, fallback.
- [ ] Phase 11 — Deployment & Environments (`docs/plan/phases/phase-11-deployment-env.md`)
  - Goals: containerization, CI/CD, secrets, domains, TLS.
- [ ] Phase 12 — UAT & Pilot Rollout (`docs/plan/phases/phase-12-uat-pilot.md`)
  - Goals: test scripts, staff training, pilot KPIs, go-live checklist.

References
- FRD: `docs/ai_appointment_booking_assistant_functional_requirements_markdown.md`
- Decisions: `docs/plan/DECISIONS.md`
- Risks: `docs/plan/RISKS.md`
