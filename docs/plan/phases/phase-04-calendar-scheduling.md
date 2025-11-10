# Phase 4 — Calendar Integration & Scheduling

Status: [~] In Progress · Owner: TBC · Target: TBC

Goals
- Check availability and create appointments with timezone handling.

Scope In
- Google Calendar API; FR datetime parsing; alternative suggestions.

Tasks
- [ ] Connect to Google Calendar (service account or OAuth as needed)
- [x] Implement availability lookup on clinic calendar (dev in-memory provider)
- [x] Parse French dates/times and convert to clinic timezone
- [x] Propose up to two alternative time slots if unavailable (dev in-memory provider)
- [x] Create calendar event with clinic + patient details (dev in-memory provider)
- [x] Handle alternative selection (patient replies 1/2)
- [ ] Update patient calendar or provide ICS invite when email unknown

Deliverables
- Scheduling module creating events after confirmation (dev flow complete with in-memory provider)

Acceptance Criteria
- Confirmed bookings create events with correct time and attendees

Metrics
- Booking success rate; reschedule rate; parsing error rate

Dependencies
- Phases 1–3; Decisions ADR-0003, ADR-0004

Links
- FRD 5.3 Scheduling
