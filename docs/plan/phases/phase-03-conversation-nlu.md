# Phase 3 — French Conversation Flow & NLU

Status: [~] In Progress · Owner: TBC · Target: TBC

Goals
- Capture name, reason, and preferred time in French with guardrails.
 - Orchestrate conversation using OpenAI Agents SDK with tool-based extraction.

Scope In
- Session state; prompts; extraction of required fields; follow-up prompts.

Tasks
- [x] Initialize OpenAI client and local connectivity test (`make agent-test`)
- [ ] Define tone and French prompts for greeting, follow-ups, and closure
- [ ] Implement session state keyed by phone number
- [ ] Define Agent tools for: field extraction, date parsing (FR), and validation
- [ ] Extract fields (name, reason, preferred time) from free text via Agent
- [ ] Validate presence; ask targeted follow-ups if missing
- [ ] Unit tests covering happy paths and edge cases

Deliverables
- Conversation module with tests and clear prompts/guardrails

Acceptance Criteria
- Typical flows capture all fields reliably in French
- Edge cases trigger targeted follow-ups

Metrics
- Field capture success rate; turns per booking; confusion/retry rate

Dependencies
- Phases 1–2; ADR-0001 accepted (Agents SDK)

Links
- FRD 5.2 Conversation Flow, 5.9 Internationalization
 - OpenAI setup: `docs/plan/SETUP_OPENAI.md`
