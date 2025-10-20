from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class NormalizedMessage:
    message_id: str
    timestamp: str
    from_waid: str
    to_phone_id: Optional[str]
    type: str
    text: Optional[str]
    contact_name: Optional[str]
    raw: Dict[str, Any]

