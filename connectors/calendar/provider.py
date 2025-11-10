from __future__ import annotations

from typing import Optional

import logging

from app.config import Settings
from connectors.calendar.base import CalendarProvider
from connectors.calendar.inmemory import store as inmemory_store

logger = logging.getLogger(__name__)

def _try_google_provider(settings: Settings):
    try:
        from connectors.calendar.google import GoogleCalendarProvider  # type: ignore

        if settings.google_creds_json and settings.google_calendar_id:
            try:
                provider = GoogleCalendarProvider(settings)
                logger.info("calendar_provider", extra={"provider": "google"})
                return provider
            except Exception as exc:  # noqa: BLE001
                logger.info("calendar_google_unavailable", extra={"error": str(exc)})
                return None
    except Exception as exc:  # noqa: BLE001
        logger.info("calendar_google_import_failed", extra={"error": str(exc)})
        return None
    return None


def get_calendar_provider(settings: Settings) -> Optional[CalendarProvider]:
    """Return a calendar provider based on configuration.

    - If Google credentials are present, a Google provider could be returned (future).
    - Otherwise, return an in-memory provider for dev/test to complete the flow.
    """
    # Prefer Google provider if configured and available, else fallback to in-memory dev provider.
    gp = _try_google_provider(settings)
    if gp is not None:
        return gp
    logger.info("calendar_provider", extra={"provider": "inmemory"})
    return inmemory_store
