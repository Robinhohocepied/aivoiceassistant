from __future__ import annotations

"""
Google Calendar provider (optional).

This provider activates when Google credentials and calendar ID are configured
AND the google libraries are installed. Otherwise, caller should fall back to
the in-memory provider.

Required packages (install when using this provider):
  pip install google-api-python-client google-auth
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from app.config import Settings
from connectors.calendar.base import CalendarEvent, CalendarProvider


def _import_google() -> Optional[Dict[str, Any]]:
    try:
        from google.oauth2.service_account import Credentials as SACredentials  # type: ignore
        from googleapiclient.discovery import build  # type: ignore
    except Exception:
        return None
    return {"SACredentials": SACredentials, "build": build}


def _load_credentials(settings: Settings):
    g = _import_google()
    if g is None:
        return None
    SACredentials = g["SACredentials"]
    # Priority: B64 -> Raw JSON -> File path
    # 1) Base64-encoded JSON
    if getattr(settings, "google_creds_json_b64", None):
        try:
            import base64, json

            decoded = base64.b64decode(settings.google_creds_json_b64.encode("utf-8")).decode("utf-8")
            data = json.loads(decoded)
            return SACredentials.from_service_account_info(
                data, scopes=["https://www.googleapis.com/auth/calendar"]
            )
        except Exception:
            # fall through to other methods
            pass

    raw = settings.google_creds_json
    if not raw:
        return None
    # 2) Inline JSON string
    if raw.strip().startswith("{"):
        import json

        data = json.loads(raw)
        return SACredentials.from_service_account_info(
            data, scopes=["https://www.googleapis.com/auth/calendar"]
        )
    # 3) Treat as file path
    return SACredentials.from_service_account_file(
        raw, scopes=["https://www.googleapis.com/auth/calendar"]
    )


class GoogleCalendarProvider(CalendarProvider):
    def __init__(self, settings: Settings) -> None:
        g = _import_google()
        if g is None:
            raise RuntimeError("Google libraries not installed")
        creds = _load_credentials(settings)
        if creds is None:
            raise RuntimeError("Google credentials not configured")
        self._build = g["build"]
        self._service = self._build("calendar", "v3", credentials=creds)
        self._calendar_id = settings.google_calendar_id or "primary"
        self._tz = settings.clinic_tz or "Europe/Brussels"
        self._send_updates = getattr(settings, "calendar_send_updates", False)

    def _overlaps(self, start: datetime, end: datetime) -> bool:
        # Query events within [start, end)
        events = (
            self._service.events()
            .list(
                calendarId=self._calendar_id,
                timeMin=start.isoformat(),
                timeMax=end.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
            .get("items", [])
        )
        return len(events) > 0

    def is_available(self, start: datetime, duration_min: int = 30) -> bool:
        end = start + timedelta(minutes=duration_min)
        return not self._overlaps(start, end)

    def suggest_alternatives(self, start: datetime, *, duration_min: int = 30, count: int = 2):
        # Try +60m, +120m, next day same hour
        from datetime import timedelta

        candidates = [start + timedelta(minutes=60), start + timedelta(minutes=120), start + timedelta(days=1)]
        out = []
        for c in candidates:
            if self.is_available(c, duration_min=duration_min):
                out.append(c)
            if len(out) >= count:
                break
        return out

    def create_event(
        self,
        start: datetime,
        *,
        duration_min: int = 30,
        title: str,
        description: Optional[str] = None,
        patient_phone: Optional[str] = None,
        patient_name: Optional[str] = None,
        patient_email: Optional[str] = None,
    ) -> CalendarEvent:
        end = start + timedelta(minutes=duration_min)
        body: Dict[str, Any] = {
            "summary": title,
            "description": description or "",
            "start": {"dateTime": start.isoformat(), "timeZone": self._tz},
            "end": {"dateTime": end.isoformat(), "timeZone": self._tz},
            "extendedProperties": {
                "private": {
                    "patient_phone": patient_phone or "",
                    "patient_name": patient_name or "",
                }
            },
        }
        attendees: list[dict] = []
        if patient_email:
            attendees.append({"email": patient_email})
        if attendees:
            body["attendees"] = attendees
        insert = self._service.events().insert(calendarId=self._calendar_id, body=body)
        if self._send_updates:
            evt = insert.sendUpdates("all").execute()  # type: ignore[attr-defined]
        else:
            evt = insert.execute()
        return CalendarEvent(
            id=evt.get("id", ""),
            start=start,
            end=end,
            title=title,
            description=description,
            patient_phone=patient_phone,
            patient_name=patient_name,
        )
