from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass
class SessionState:
    from_waid: str
    name: Optional[str] = None
    reason: Optional[str] = None
    email: Optional[str] = None
    preferred_time: Optional[str] = None
    preferred_time_iso: Optional[str] = None
    event_id: Optional[str] = None
    pending_alternatives: Optional[List[str]] = None
    pending_duration_min: Optional[int] = None
    # Flow V2 fields
    stage: Optional[str] = None
    dob: Optional[str] = None
    service: Optional[str] = None
    douleur_score: Optional[int] = None
    red_flags: Optional[bool] = None
    date_cible_text: Optional[str] = None
    plage_horaire: Optional[str] = None
    slots_offered: Optional[List[str]] = None
    stop_opt_out: bool = False
    failed_identity: int = 0
    # Classic flow (extraction) – track which fields we've already prompted for
    prompted_fields: Optional[List[str]] = None


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
