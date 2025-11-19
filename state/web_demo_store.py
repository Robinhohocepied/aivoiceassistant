from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional, Set

from agents.session import SessionState


@dataclass
class DemoSessionMeta:
    session_id: str
    date_key: str
    started_at: datetime
    message_count: int = 0


class WebDemoStore:
    def __init__(self) -> None:
        self._states: Dict[str, SessionState] = {}
        self._meta: Dict[str, DemoSessionMeta] = {}
        self._by_date: Dict[str, Set[str]] = {}

    def get(self, session_id: str) -> Optional[SessionState]:
        return self._states.get(session_id)

    def put(self, session_id: str, state: SessionState) -> None:
        self._states[session_id] = state

    def touch_message(self, session_id: str) -> None:
        if session_id in self._meta:
            self._meta[session_id].message_count += 1

    def start_if_allowed(self, session_id: str, *, date_key: str, max_per_day: int) -> bool:
        # Already exists counts as allowed (not a new start)
        if session_id in self._meta:
            return True
        started_set = self._by_date.setdefault(date_key, set())
        if len(started_set) >= max_per_day:
            return False
        # Start a new meta record
        self._meta[session_id] = DemoSessionMeta(session_id=session_id, date_key=date_key, started_at=datetime.utcnow())
        started_set.add(session_id)
        return True

    def count_for_date(self, date_key: str) -> int:
        return len(self._by_date.get(date_key, set()))

    def get_meta(self, session_id: str) -> Optional[DemoSessionMeta]:
        return self._meta.get(session_id)

    def cleanup(self, ttl_hours: int = 48) -> None:
        cutoff = datetime.utcnow() - timedelta(hours=ttl_hours)
        to_delete = [sid for sid, meta in self._meta.items() if meta.started_at < cutoff]
        for sid in to_delete:
            meta = self._meta.pop(sid)
            self._states.pop(sid, None)
            if meta and meta.date_key in self._by_date and sid in self._by_date[meta.date_key]:
                self._by_date[meta.date_key].remove(sid)


store = WebDemoStore()

