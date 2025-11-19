from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.config import load_settings
from engine.core import run_engine
from engine.types import EngineMessage
from state.web_demo_store import store as demo_store
from agents.session import SessionState


router = APIRouter(prefix="/api/v1", tags=["web_demo"])


@router.post("/demo-chat")
def demo_chat(payload: Dict[str, Any]) -> Dict[str, Any]:  # type: ignore
    s = load_settings()
    session_id = str(payload.get("session_id") or "").strip()
    text = str(payload.get("text") or "").strip()
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    # Daily limit enforcement for new sessions
    tz = ZoneInfo(getattr(s, "demo_timezone", "Europe/Amsterdam"))
    today = datetime.now(tz).date()
    date_key = today.isoformat()
    max_per_day = getattr(s, "demo_daily_limit", 20)
    ttl_hours = getattr(s, "demo_session_ttl_hours", 48)
    max_messages = getattr(s, "max_messages_per_demo_session", 40)

    # Cleanup old demo sessions opportunistically
    demo_store.cleanup(ttl_hours=ttl_hours)

    state = demo_store.get(session_id)
    if state is None:
        if not demo_store.start_if_allowed(session_id, date_key=date_key, max_per_day=max_per_day):
            return {
                "ok": True,
                "limit_reached": True,
                "messages": [
                    {"type": "text", "text": "Limite quotidienne atteinte. Merci de revenir demain 🙏"}
                ],
                "done": True,
                "session_id": session_id,
            }
        # Create initial state
        state = SessionState(from_waid=session_id)
        state.stage = None
        demo_store.put(session_id, state)

    # Message cap enforcement
    meta = demo_store.get_meta(session_id)
    if meta and meta.message_count >= max_messages:
        return {
            "ok": True,
            "messages": [
                {"type": "text", "text": "Cette démonstration est terminée, merci 🙏"}
            ],
            "done": True,
            "session_id": session_id,
        }

    # Run engine
    result = run_engine(channel="web_demo", session_state=state, user_text=text, settings=s)

    # Increment message count and persist state
    demo_store.touch_message(session_id)
    demo_store.put(session_id, result.state or state)

    out_msgs = [{"type": m.type, "text": m.text} for m in result.messages]
    out_opts = [{"id": o.id, "label": o.label} for o in result.options]

    return {
        "ok": True,
        "messages": out_msgs,
        "options": out_opts,
        "done": result.signals.done,
        "limit_reached": result.signals.limit_reached,
        "session_id": session_id,
    }

