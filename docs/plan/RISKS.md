# Risk Register

Track risks with mitigation plans. Update status regularly.

- R-01: WhatsApp API rate limiting or outages
  - Impact: Medium · Likelihood: Medium
  - Mitigation: Retries with backoff; alert on failures; fallback to human.

- R-02: NLU misinterpretation of French free-text
  - Impact: High · Likelihood: Medium
  - Mitigation: Clear prompts/guardrails; targeted follow-ups; unit tests on edge cases.

- R-03: Timezone and FR date parsing errors
  - Impact: High · Likelihood: Medium
  - Mitigation: Use robust parser; default to Europe/Brussels; confirm with patient when ambiguous.

- R-04: Google Calendar permissions and event visibility
  - Impact: Medium · Likelihood: Medium
  - Mitigation: Validate scopes early; service account sharing; ICS fallback to patients.

- R-05: GDPR non-compliance (consent, deletion)
  - Impact: High · Likelihood: Low/Medium
  - Mitigation: Consent flow; deletion automation within 24h; PII masking in logs.

- R-06: Reminder delivery failures (T-24h)
  - Impact: Medium · Likelihood: Medium
  - Mitigation: Delivery receipts; retry queue; manual backup reminder process.

- R-07: Emergency handoff delays
  - Impact: High · Likelihood: Low
  - Mitigation: SMS/Email alert with escalation chain; SLA monitoring.

- R-08: Secrets leakage or misconfiguration
  - Impact: High · Likelihood: Low
  - Mitigation: Use env vars/secrets manager; never log secrets; rotate regularly.

- R-09: Scalability under concurrent conversations
  - Impact: Medium · Likelihood: Medium
  - Mitigation: Async I/O; stateless handlers; session store; load test.

- R-10: Patient identity mismatch (wrong calendar/email)
  - Impact: Medium · Likelihood: Low
  - Mitigation: Confirm email/phone; include context in booking summary; clinic verification.

