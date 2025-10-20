import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore


WEEKDAYS = {
    "lundi": 0,
    "mardi": 1,
    "mercredi": 2,
    "jeudi": 3,
    "vendredi": 4,
    "samedi": 5,
    "dimanche": 6,
}


@dataclass
class ParsedTime:
    iso: Optional[str]
    note: Optional[str] = None


def _next_weekday(now: datetime, target: int, week_offset: int = 0) -> datetime:
    days_ahead = (target - now.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7  # next occurrence, not today
    days_ahead += 7 * week_offset
    return now + timedelta(days=days_ahead)


def parse_preferred_time_fr(
    text: str,
    *,
    now: Optional[datetime] = None,
    tz: str = "Europe/Brussels",
) -> ParsedTime:
    s = text.lower()
    tzinfo = ZoneInfo(tz) if ZoneInfo else None
    ref = now or datetime.now(tzinfo)

    # Relative days
    if "aujourd'hui" in s or "aujourd" in s:
        day = ref
    elif "après-demain" in s or "apres-demain" in s:
        day = ref + timedelta(days=2)
    elif "demain" in s:
        day = ref + timedelta(days=1)
    else:
        # Days of week (with optional "prochain")
        week_offset = 1 if "prochain" in s else 0
        day = None
        for name, wd in WEEKDAYS.items():
            if name in s:
                base = _next_weekday(ref, wd, week_offset)
                day = base
                break
        if day is None:
            day = ref  # fallback to today

    # Time of day keywords
    hour = None
    minute = 0
    if "matin" in s:
        hour = 9
    elif "après-midi" in s or "apres-midi" in s:
        hour = 14
    elif "soir" in s:
        hour = 18

    # Explicit times like 10h, 10:30, 10 h 15
    m = re.search(r"(\d{1,2})\s*(?:h|:\s?)(\d{0,2})?", s)
    if m:
        hour = int(m.group(1))
        if hour > 23:
            hour = hour % 24
        if m.group(2):
            minute = int(m.group(2))

    # If no hour specified, default to 10:00
    if hour is None:
        hour = 10

    dt = day.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if tzinfo and dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzinfo)
    return ParsedTime(iso=dt.isoformat(), note=None)

