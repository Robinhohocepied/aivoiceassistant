from __future__ import annotations

from typing import Optional, List

from app.config import Settings
from engine.types import EngineResult, EngineMessage, EngineOption
from agents.flow_v2 import handle_message as flow2_handle


def run_engine(
    *,
    channel: str,
    session_state,  # SessionState-like object
    user_text: str,
    settings: Settings,
) -> EngineResult:
    """Channel-agnostic conversation engine.

    Currently delegates to Flow V2 logic and normalizes outputs to a generic schema.
    """
    out = flow2_handle(user_text, session_state, settings)
    result = EngineResult(state=session_state)
    if not out:
        return result
    if isinstance(out, dict):
        t = out.get("type")
        if t == "service_buttons":
            # Add a leading text message explaining the selection
            txt = str(out.get("text") or "")
            if txt:
                result.messages.append(EngineMessage(text=txt))
            for b in list(out.get("buttons") or [])[:3]:
                result.options.append(EngineOption(id=b.get("id") or "", label=b.get("title") or ""))
        else:
            # Unknown dict payload; stringify
            result.messages.append(EngineMessage(text=str(out)))
    else:
        result.messages.append(EngineMessage(text=str(out)))
    return result

