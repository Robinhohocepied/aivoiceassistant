# Master TODO Tracker

Cross-phase checklist. Update alongside per-phase trackers.

Foundations
- [x] Select stack and confirm with stakeholders (FastAPI + OpenAI Agents SDK)
- [x] Define repo layout and scaffolding
- [x] Add `.env.example` and secret loading pattern
- [x] Health endpoint and basic CI (lint/test)
- [x] Structured logging with PII redaction

WhatsApp Integration
- [x] Webhook verification (GET) and inbound handler (POST)
- [x] Send API wrapper with retry/backoff
- [x] Normalize inbound messages; persist envelopes (in-memory)
- [x] Sandbox setup and documentation

Conversation & NLU (French)
- [x] Initialize OpenAI client and connectivity test
- [x] Session state by phone number
- [x] Structured extraction to JSON (name, reason, preferred_time)
- [x] FR datetime normalization baseline (preferred_time_iso)
- [ ] Prompting + guardrails in French (tone, safety)
- [ ] Tests for edge cases and ambiguous time expressions

Calendar & Scheduling
- [ ] Google Calendar auth and connectivity
- [x] Availability lookup for clinic calendar (dev in-memory provider)
- [x] FR datetime parsing; timezone conversion (Europe/Brussels)
- [x] Offer up to 2 alternatives when unavailable (dev in-memory provider)
- [x] Create events with clinic + patient details (dev in-memory provider)
- [x] Handle user selection of alternatives via numeric reply (1/2)

Confirmations & Reminders
- [x] Booking summary via WhatsApp (post-booking message)
- [ ] ICS fallback when email missing
- [ ] Reminder scheduler at T-24h
- [x] FR locale formatting (basic humanized date)

Rescheduling & Cancellation
- [ ] Detect “modifier” and “annuler”
- [ ] Locate event; propose slots or delete
- [ ] Update calendars; notify clinic; audit trail

Emergency & Handoff
- [ ] Detect “URGENT” and synonyms
- [ ] Alert staff (Slack/Email/SMS)
- [ ] Pause/resume automation mechanics

Privacy & GDPR
- [ ] Consent flow + privacy policy link
- [ ] Data minimization + retention config
- [ ] PII masking in logs; encryption at rest (where applicable)
- [ ] “Delete my data” within 24h with proof

Logging, Monitoring & Analytics
- [ ] Correlation IDs and tracing
- [ ] Booking funnel metrics
- [ ] Alerts for errors and availability

Performance & Reliability
- [ ] ≤5s median response time
- [ ] Retries/backoff; idempotency keys
- [ ] Fallback to human on repeated failures

Deployment & Environments
- [ ] Containerization and env configs
- [ ] CI/CD + secrets management
- [ ] HTTPS for webhooks; token rotation

UAT & Pilot
- [ ] Test scripts (FR scenarios)
- [ ] Staff training + escalation playbook
- [ ] Pilot KPIs and go/no-go
