import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)


class WhatsAppClient:
    def __init__(self, token: str, phone_id: str, base_url: str) -> None:
        self.token = token
        self.phone_id = phone_id
        self.base_url = base_url.rstrip("/")

    @property
    def messages_url(self) -> str:
        return f"{self.base_url}/{self.phone_id}/messages"

    async def send_text(self, to: str, body: str, dry_run: bool = False) -> Dict[str, Any]:
        to_sanitized = "".join(ch for ch in to if ch.isdigit())
        payload = {
            "messaging_product": "whatsapp",
            "to": to_sanitized,
            "type": "text",
            "text": {"body": body},
        }
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

        if dry_run:
            logger.info("whatsapp send dry_run", extra={"to": to, "preview": payload})
            return {"dry_run": True, "payload": payload}

        # Simple retry/backoff
        delay = 0.5
        last_exc: Optional[Exception] = None
        for _ in range(3):
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.post(self.messages_url, headers=headers, json=payload)
                    resp.raise_for_status()
                    return resp.json()
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                logger.warning("whatsapp send failed, retrying", extra={"error": str(exc)})
                await asyncio.sleep(delay)
                delay *= 2
        assert last_exc is not None
        raise last_exc


def from_settings(settings: Settings) -> Optional[WhatsAppClient]:
    if not settings.whatsapp_token or not settings.whatsapp_phone_id:
        return None
    return WhatsAppClient(
        token=settings.whatsapp_token,
        phone_id=settings.whatsapp_phone_id,
        base_url=settings.whatsapp_base_url,
    )
