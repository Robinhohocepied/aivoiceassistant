from __future__ import annotations

import itertools
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from connectors.calendar.base import CalendarEvent, CalendarProvider


class InMemoryCalendar(CalendarProvider):
    """Simple in-memory calendar for dev/test.

    Not thread-safe and not persistent. Good enough for local E2E.
    """

    def __init__(self) -> None:
        self._events: List[CalendarEvent] = []

    def _overlaps(self, start: datetime, end: datetime) -> bool:
        for e in self._events:
            if not (end <= e.start or start >= e.end):
                return True
        return False

    def is_available(self, start: datetime, duration_min: int = 30) -> bool:
        end = start + timedelta(minutes=duration_min)
        return not self._overlaps(start, end)

    def suggest_alternatives(
        self, start: datetime, *, duration_min: int = 30, count: int = 2
    ) -> List[datetime]:
        """Return up to `count` alternative start times near the requested one.

        Strategy: try +60m, +120m, next day at same hour, then next day +60m, etc.
        """
        candidates: List[datetime] = []
        base = start
        deltas = [60, 120, 24 * 60, 24 * 60 + 60, 24 * 60 + 120, 2 * 24 * 60]
        for minutes in deltas:
            candidates.append(base + timedelta(minutes=minutes))
        out: List[datetime] = []
        for c in candidates:
            if self.is_available(c, duration_min=duration_min):
                out.append(c)
            if len(out) >= count:
                break
        return out

    def create_event(
        self,
        start: datetime,
        *,
        duration_min: int = 30,
        title: str,
        description: Optional[str] = None,
        patient_phone: Optional[str] = None,
        patient_name: Optional[str] = None,
    ) -> CalendarEvent:
        end = start + timedelta(minutes=duration_min)
        evt = CalendarEvent(
            id=str(uuid.uuid4()),
            start=start,
            end=end,
            title=title,
            description=description,
            patient_phone=patient_phone,
            patient_name=patient_name,
        )
        self._events.append(evt)
        return evt


# Singleton instance for app usage
store = InMemoryCalendar()

