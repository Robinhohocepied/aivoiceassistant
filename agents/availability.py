from __future__ import annotations

from datetime import datetime, timedelta
from typing import List
from zoneinfo import ZoneInfo


def _is_working_time(dt: datetime) -> bool:
    # Mon-Fri, 09:00-12:00 and 14:00-18:00
    if dt.weekday() >= 5:
        return False
    h = dt.hour
    if 9 <= h < 12:
        return True
    if 14 <= h < 18:
        return True
    return False


def next_slots(tz_name: str, count: int = 3, slot_minutes: int = 30) -> List[str]:
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)
    # Round up to next 15-min boundary
    minutes = ((now.minute // 15) + 1) * 15
    candidate = now.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minutes)

    slots: List[str] = []
    step = timedelta(minutes=slot_minutes)
    guard = 0
    while len(slots) < count and guard < 2000:
        guard += 1
        if _is_working_time(candidate):
            slots.append(candidate.isoformat())
        candidate += step
    return slots
