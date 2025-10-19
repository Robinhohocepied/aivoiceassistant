import logging

from app.config import Settings
from connectors.whatsapp.types import NormalizedMessage

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

