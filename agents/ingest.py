import logging

from app.config import Settings
from connectors.whatsapp.types import NormalizedMessage
from connectors.whatsapp.client import from_settings as whatsapp_client_from_settings
from .reply import generate_reply
from .state import get_conversation
from .availability import next_slots

logger = logging.getLogger(__name__)


async def handle_inbound_message(msg: NormalizedMessage, settings: Settings) -> None:
    """Stub integration point that will later call the Agents SDK.

    For Phase 2, we only log and no-op to keep webhook latency minimal.
    """
    # Log minimal details inline so they appear in JSON logs
    logger.info("agent_ingest from=%s type=%s text=%s", msg.from_waid, msg.type, msg.text)

    # Optional auto-reply via OpenAI + WhatsApp (dev/proto only)
    if not settings.whatsapp_autoreply:
        return

    if msg.type != "text" or not msg.text:
        return

    # Update conversation state and gather context
    conv = get_conversation(msg.from_waid)
    conv.append("user", msg.text)
    slots = next_slots(settings.clinic_tz, count=3)

    # Create reply
    reply_text = await generate_reply(msg.text, settings, history=conv.recent(), availability_slots=slots)
    if not reply_text:
        return

    # Send via WhatsApp if configured
    client = whatsapp_client_from_settings(settings)
    if client is None:
        logger.info("whatsapp client not configured; skip send")
        return

    try:
        result = await client.send_text(to=msg.from_waid, body=reply_text, dry_run=settings.whatsapp_dry_run)
        conv.append("assistant", reply_text)
        logger.info("whatsapp send", extra={"to": msg.from_waid, "dry_run": settings.whatsapp_dry_run})
    except Exception as exc:  # noqa: BLE001
        logger.exception("whatsapp send failed: %s", exc)
