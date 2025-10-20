# Phase 4 — Calendar Integration & Scheduling

Status: [ ] Not Started · Owner: TBC · Target: TBC

Goals
- Check availability and create appointments with timezone handling.

Scope In
- Google Calendar API; FR datetime parsing; alternative suggestions.

Tasks
- [ ] Connect to Google Calendar (service account or OAuth as needed)
- [ ] Implement availability lookup on clinic calendar
- [ ] Parse French dates/times and convert to clinic timezone
- [ ] Propose up to two alternative time slots if unavailable
- [ ] Create calendar event with clinic + patient details
- [ ] Update patient calendar or provide ICS invite when email unknown

Deliverables
- Scheduling module creating events after confirmation

Acceptance Criteria
- Confirmed bookings create events with correct time and attendees

Metrics
- Booking success rate; reschedule rate; parsing error rate

Dependencies
- Phases 1–3; Decisions ADR-0003, ADR-0004

Links
- FRD 5.3 Scheduling

