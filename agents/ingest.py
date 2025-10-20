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
from agents.datetime_fr import parse_preferred_time_fr

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
    # Robust parameter fallback loop for model/SDK differences
    use_response_format = True
    use_temperature = True
    use_max_tokens = True
    text_out: Optional[str] = None
    for _ in range(4):
        try:
            kwargs: Dict[str, Any] = {
                "model": settings.agent_model,
                "input": messages,
                "metadata": {"source": "whatsapp", "from": msg.from_waid},
            }
            if use_response_format:
                kwargs["response_format"] = {"type": "json_object"}
            if use_temperature:
                kwargs["temperature"] = 0.2
            if use_max_tokens:
                kwargs["max_output_tokens"] = 200
            resp = client.responses.create(**kwargs)
            text_out = getattr(resp, "output_text", None) or str(resp)
            break
        except TypeError as te:
            # Older SDKs: drop response_format
            if "response_format" in str(te) and use_response_format:
                use_response_format = False
                logger.info("agent_call_retry", extra={"reason": "no_response_format"})
                continue
            logger.exception("agent model call failed: %s", te)
            return
        except Exception as exc:  # noqa: BLE001
            msg_exc = str(exc)
            if "Unsupported parameter" in msg_exc and "temperature" in msg_exc and use_temperature:
                use_temperature = False
                logger.info("agent_call_retry", extra={"reason": "no_temperature"})
                continue
            if "Unsupported parameter" in msg_exc and "max_output_tokens" in msg_exc and use_max_tokens:
                use_max_tokens = False
                logger.info("agent_call_retry", extra={"reason": "no_max_tokens"})
                continue
            logger.exception("agent model call failed: %s", exc)
            return
    if text_out is None:
        return

    # Parse and merge extraction
    extracted_dict = try_parse_json(text_out) or {}
    try:
        extracted_model = Extraction.model_validate(extracted_dict)
        extracted = extracted_model.model_dump()
    except Exception:
        extracted = extracted_dict
    state = merge_extracted(state, extracted)
    # Normalize preferred_time if present
    if state.preferred_time and not state.preferred_time_iso:
        try:
            parsed = parse_preferred_time_fr(state.preferred_time)
            state.preferred_time_iso = parsed.iso
        except Exception as exc:  # noqa: BLE001
            logger.warning("preferred_time_parse_failed", extra={"error": str(exc)})
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
