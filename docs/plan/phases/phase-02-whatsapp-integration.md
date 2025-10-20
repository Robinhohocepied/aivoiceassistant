# Phase 2 — WhatsApp Messaging Integration

Status: [~] In Progress · Owner: TBC · Target: TBC

Goals
- Receive and send WhatsApp messages via Cloud API with basic traceability.
 - Prepare outbound/inbound adapters to interface with the OpenAI Agents SDK orchestrator (Phase 3).

Scope In
- Webhook verification and inbound POST handling; send wrapper; sandbox.

Tasks
- [x] Implement webhook verification (GET) using `WHATSAPP_VERIFY_TOKEN`
- [x] Handle inbound messages (POST) and normalize payloads
- [x] Implement send API wrapper with retry/backoff and error handling
- [x] Persist message envelopes with correlation IDs (in-memory Phase 2)
- [x] Configure sandbox phone and verify delivery (ngrok + Meta Webhooks)
- [x] Document webhook setup (HTTPS, callback URL)
- [x] Define integration point (function/callback) to pass/receive messages to/from Agents SDK
 - [x] Add local dev debugging aids (structured logs with text/from; `GET /webhooks/whatsapp/_debug/messages`)

Deliverables
- Working inbound WhatsApp integration in sandbox with normalized storage and clear logs
- Outbound client wrapper available (not yet wired to auto-reply)
- Documentation for local ngrok and webhook setup

Acceptance Criteria
- Webhook verified successfully; inbound messages received and visible in logs/debug endpoint
- Outbound responses delivered to sandbox device (Pending wiring to flows)

Metrics
- Delivery success rate; latency; error rates by endpoint

Dependencies
- Phase 1 foundations
- Decisions ADR-0002; ADR-0001 accepted (Agents SDK)

Links
- FRD 5.1 Messaging
- Local ngrok: `docs/plan/SETUP_NGROK.md`
- Decisions: `docs/plan/DECISIONS.md#adr-0002-messaging-provider`
