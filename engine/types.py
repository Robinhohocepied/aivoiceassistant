from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class EngineMessage:
    type: str = "text"
    text: str = ""


@dataclass
class EngineOption:
    id: str
    label: str


@dataclass
class EngineSignals:
    done: bool = False
    limit_reached: bool = False
    error: Optional[str] = None


@dataclass
class EngineResult:
    messages: List[EngineMessage] = field(default_factory=list)
    options: List[EngineOption] = field(default_factory=list)
    signals: EngineSignals = field(default_factory=EngineSignals)
    state: Optional[Any] = None

