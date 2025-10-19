import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.config import Settings, load_settings

from .store import store
from .types import NormalizedMessage

logger = logging.getLogger(__name__)


def get_settings() -> Settings:
    return load_settings()


def get_router(settings: Optional[Settings] = None) -> APIRouter:
    s = settings or load_settings()
    router = APIRouter(prefix="/webhooks/whatsapp", tags=["whatsapp"])

    @router.get("")
    async def verify(
        hub_mode: Optional[str] = Query(None, alias="hub.mode"),
        hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
        hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    ) -> PlainTextResponse:  # type: ignore
        if hub_mode == "subscribe" and hub_verify_token and hub_challenge:
            if s.whatsapp_verify_token and hub_verify_token == s.whatsapp_verify_token:
                return PlainTextResponse(hub_challenge)
        raise HTTPException(status_code=403, detail="Forbidden")

    @router.post("")
    async def inbound(request: Request) -> PlainTextResponse:  # type: ignore
        payload: Dict[str, Any] = await request.json()
        normalized = normalize_inbound(payload)
        for msg in normalized:
            store.save(msg)
            try:
                # Integration hook for Phase 3: route to Agents SDK (stub)
                from agents.ingest import handle_inbound_message  # local import to avoid cycle

                await handle_inbound_message(msg, s)
            except Exception as exc:  # noqa: BLE001
                logger.exception("agent ingestion failed: %s", exc)
        return PlainTextResponse("EVENT_RECEIVED")

    return router


def normalize_inbound(payload: Dict[str, Any]) -> List[NormalizedMessage]:
    out: List[NormalizedMessage] = []
    entries = payload.get("entry") or []
    for entry in entries:
        changes = entry.get("changes") or []
        for change in changes:
            value = change.get("value") or {}
            metadata = value.get("metadata") or {}
            to_phone_id = metadata.get("phone_number_id")
            contacts = value.get("contacts") or []
            contact_name = None
            if contacts:
                contact_name = (contacts[0].get("profile") or {}).get("name")
            messages = value.get("messages") or []
            for m in messages:
                m_type = m.get("type")
                text_body = None
                if m_type == "text":
                    text = m.get("text") or {}
                    text_body = text.get("body")
                out.append(
                    NormalizedMessage(
                        message_id=m.get("id") or "",
                        timestamp=m.get("timestamp") or "",
                        from_waid=m.get("from") or contacts[0].get("wa_id") if contacts else "",
                        to_phone_id=to_phone_id,
                        type=m_type or "",
                        text=text_body,
                        contact_name=contact_name,
                        raw=m,
                    )
                )
    return out
