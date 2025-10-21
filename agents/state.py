from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Tuple


Message = Tuple[str, str]  # (role, content) where role in {"user", "assistant"}


@dataclass
class ConversationState:
    waid: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    history: List[Message] = field(default_factory=list)

    def append(self, role: str, content: str) -> None:
        self.history.append((role, content))
        self.updated_at = datetime.now(timezone.utc)

    def recent(self, limit: int = 8) -> List[Message]:
        return self.history[-limit:]


_CONV: Dict[str, ConversationState] = {}


def get_conversation(waid: str) -> ConversationState:
    state = _CONV.get(waid)
    if state is None:
        state = ConversationState(waid=waid)
        _CONV[waid] = state
    return state


def clear_conversation(waid: str) -> None:
    _CONV.pop(waid, None)

