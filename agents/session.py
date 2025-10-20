from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class SessionState:
    from_waid: str
    name: Optional[str] = None
    reason: Optional[str] = None
    preferred_time: Optional[str] = None
    preferred_time_iso: Optional[str] = None


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, SessionState] = {}

    def get(self, waid: str) -> SessionState:
        if waid not in self._sessions:
            self._sessions[waid] = SessionState(from_waid=waid)
        return self._sessions[waid]

    def put(self, state: SessionState) -> None:
        self._sessions[state.from_waid] = state

    def clear(self, waid: Optional[str] = None) -> None:
        if waid is None:
            self._sessions.clear()
        else:
            self._sessions.pop(waid, None)


store = InMemorySessionStore()
