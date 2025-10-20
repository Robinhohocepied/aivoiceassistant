# Phase 3 — French Conversation Flow & NLU

Status: [~] In Progress · Owner: TBC · Target: TBC

Goals
- Capture name, reason, and preferred time in French with guardrails.
 - Orchestrate conversation using OpenAI Agents SDK with tool-based extraction.

Scope In
- Session state; prompts; extraction of required fields; follow-up prompts.

Tasks
- [x] Initialize OpenAI client and local connectivity test (`make agent-test`)
- [x] Implement session state keyed by phone number
- [x] Extract fields (name, reason, preferred time) to JSON (structured outputs)
- [x] Normalize preferred_time → ISO (baseline FR parser)
- [ ] Define tone and French prompts for greeting, follow-ups, and closure
- [ ] Validate presence; ask targeted follow-ups if missing (expand variants)
- [ ] Unit tests for edge cases and ambiguous time expressions

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
