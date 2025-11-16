from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional


@dataclass
class CalendarEvent:
    id: str
    start: datetime
    end: datetime
    title: str
    description: Optional[str] = None
    patient_phone: Optional[str] = None
    patient_name: Optional[str] = None


class CalendarProvider:
    """Abstract calendar provider interface.

    Implementations should handle availability checks and event creation.
    All datetimes MUST be timezone-aware.
    """

    def is_available(self, start: datetime, duration_min: int = 30) -> bool:  # pragma: no cover - interface
        raise NotImplementedError

    def suggest_alternatives(
        self, start: datetime, *, duration_min: int = 30, count: int = 2
    ) -> List[datetime]:  # pragma: no cover - interface
        raise NotImplementedError

    def create_event(
        self,
        start: datetime,
        *,
        duration_min: int = 30,
        title: str,
        description: Optional[str] = None,
        patient_phone: Optional[str] = None,
        patient_name: Optional[str] = None,
        patient_email: Optional[str] = None,
    ) -> CalendarEvent:  # pragma: no cover - interface
        raise NotImplementedError
