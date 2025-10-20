import logging
from typing import Optional

from app.config import Settings, load_settings
from connectors.whatsapp.types import NormalizedMessage
from agents.client import create_agents_client
from agents.session import store as session_store
from agents.conversation import (
    build_messages,
    try_parse_json,
    merge_extracted,
    compose_followup,
)
from connectors.whatsapp.client import from_settings as whatsapp_from_settings
from agents.schemas import Extraction

logger = logging.getLogger(__name__)


async def handle_inbound_message(msg: NormalizedMessage, settings: Settings) -> None:
    """Stub integration point that will later call the Agents SDK.

    For Phase 2, we only log and no-op to keep webhook latency minimal.
    """
    logger.info(
        "agent_ingest",
        extra={
            "from": msg.from_waid,
            "text": msg.text,
            "type": msg.type,
        },
    )

    # Only process text messages in Phase 3
    if msg.type != "text" or not msg.text:
        return

    client = create_agents_client(settings)
    if client is None:
        # Agents not configured; only log
        return

    # Retrieve session and build prompt/messages
    state = session_store.get(msg.from_waid)
    messages = build_messages(msg.text, state)

    # Call the model
    try:
        resp = client.responses.create(
            model=settings.agent_model,
            input=messages,
            temperature=0.2,
            max_output_tokens=200,
            response_format={"type": "json_object"},
            metadata={"source": "whatsapp", "from": msg.from_waid},
        )
        text_out: str = getattr(resp, "output_text", None) or str(resp)
    except Exception as exc:  # noqa: BLE001
        logger.exception("agent model call failed: %s", exc)
        return

    # Parse and merge extraction
    extracted_dict = try_parse_json(text_out) or {}
    try:
        extracted_model = Extraction.model_validate(extracted_dict)
        extracted = extracted_model.model_dump()
    except Exception:
        extracted = extracted_dict
    state = merge_extracted(state, extracted)
    session_store.put(state)

    # Compose follow-up/confirmation
    reply = compose_followup(state)

    # Optionally auto-reply via WhatsApp
    if settings.agent_auto_reply:
        try:
            wa_client = whatsapp_from_settings(settings)
            if wa_client is None:
                logger.info("auto_reply_skipped", extra={"reason": "whatsapp_client_unconfigured"})
                return
            result = await wa_client.send_text(to=msg.from_waid, body=reply, dry_run=settings.agent_dry_run)
            logger.info("auto_reply", extra={"to": msg.from_waid, "dry_run": settings.agent_dry_run, "result": str(result)})
        except Exception as exc:  # noqa: BLE001
            logger.exception("auto-reply failed: %s", exc)
