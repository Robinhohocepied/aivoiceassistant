import asyncio
import json

import pytest

from app.config import load_settings
from agents.session import store as session_store
from connectors.whatsapp.types import NormalizedMessage
from agents.ingest import handle_inbound_message


class _StubWA:
    def __init__(self) -> None:
        self.sent = []

    async def send_text(self, to: str, body: str, dry_run: bool = False):  # type: ignore[no-untyped-def]
        self.sent.append({"to": to, "body": body, "dry_run": dry_run})
        return {"ok": True, "dry_run": dry_run}


class _StubResp:
    def __init__(self, text: str) -> None:
        self.output_text = text


class _StubClient:
    class _Responses:
        def __init__(self, payload: str) -> None:
            self._payload = payload

        def create(self, **kwargs):  # type: ignore[no-untyped-def]
            return _StubResp(self._payload)

    def __init__(self, payload: str) -> None:
        self.responses = self._Responses(payload)


def _fixed_parse(_text: str):
    # Fixed ISO for deterministic tests: Tuesday 2025-01-14 10:30+01:00
    return type("P", (), {"iso": "2025-01-14T10:30:00+01:00"})()


def test_booking_success_with_inmemory_calendar(monkeypatch):
    session_store.clear()
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("AGENT_AUTO_REPLY", "true")
    monkeypatch.setenv("AGENT_DRY_RUN", "true")

    # Extraction returns completed fields
    payload = json.dumps({
        "name": "Alice",
        "reason": "Controle",
        "preferred_time": "mardi 10h30",
    })
    monkeypatch.setattr("agents.ingest.create_agents_client", lambda settings: _StubClient(payload), raising=True)
    monkeypatch.setattr("agents.ingest.parse_preferred_time_fr", _fixed_parse, raising=True)

    # WhatsApp stub
    wa_stub = _StubWA()
    monkeypatch.setattr("agents.ingest.whatsapp_from_settings", lambda s: wa_stub, raising=True)

    s = load_settings()
    msg = NormalizedMessage(
        message_id="wamid.ABC",
        timestamp="0",
        from_waid="+32000000000",
        to_phone_id="PHONE",
        type="text",
        text="Bonjour, mardi 10h30 ca me va.",
        contact_name="Alice",
        raw={},
    )
    asyncio.run(handle_inbound_message(msg, s))

    st = session_store.get("+32000000000")
    assert st.event_id is not None
    assert wa_stub.sent, "auto-reply should send a message"
    assert "Date:" in wa_stub.sent[0]["body"] and "Vous recevrez" in wa_stub.sent[0]["body"]


def test_booking_unavailable_offers_alternatives(monkeypatch):
    session_store.clear()
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("AGENT_AUTO_REPLY", "true")
    monkeypatch.setenv("AGENT_DRY_RUN", "true")

    # Extraction returns completed fields
    payload = json.dumps({
        "name": "Bob",
        "reason": "Visite",
        "preferred_time": "mardi 10h30",
    })
    monkeypatch.setattr("agents.ingest.create_agents_client", lambda settings: _StubClient(payload), raising=True)
    monkeypatch.setattr("agents.ingest.parse_preferred_time_fr", _fixed_parse, raising=True)

    # WhatsApp stub
    wa_stub = _StubWA()
    monkeypatch.setattr("agents.ingest.whatsapp_from_settings", lambda s: wa_stub, raising=True)

    # Monkeypatch calendar provider to be unavailable at requested time but available later
    from datetime import datetime, timedelta

    class _BusyFirst:
        def is_available(self, start: datetime, duration_min: int = 30) -> bool:
            # Busy exactly at requested fixed time
            return start.isoformat() != "2025-01-14T10:30:00+01:00"

        def suggest_alternatives(self, start: datetime, *, duration_min: int = 30, count: int = 2):
            return [start + timedelta(minutes=60), start + timedelta(minutes=120)]

        def create_event(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            raise AssertionError("should not be called in unavailable case")

    monkeypatch.setattr("agents.ingest.get_calendar_provider", lambda s: _BusyFirst(), raising=True)

    s = load_settings()
    msg = NormalizedMessage(
        message_id="wamid.DEF",
        timestamp="0",
        from_waid="+32000000001",
        to_phone_id="PHONE",
        type="text",
        text="Bonjour, mardi 10h30 svp.",
        contact_name="Bob",
        raw={},
    )
    asyncio.run(handle_inbound_message(msg, s))

    st = session_store.get("+32000000001")
    assert st.event_id is None
    assert wa_stub.sent, "auto-reply should send a message"
    body = wa_stub.sent[0]["body"]
    assert "Propositions" in body and ("1)" in body or "2)" in body)


def test_booking_from_selection_of_alternative(monkeypatch):
    # Step 1: Propose alternatives
    session_store.clear()
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("AGENT_AUTO_REPLY", "true")
    monkeypatch.setenv("AGENT_DRY_RUN", "true")

    payload = json.dumps({
        "name": "Cara",
        "reason": "Consultation",
        "preferred_time": "mardi 10h30",
    })
    monkeypatch.setattr("agents.ingest.create_agents_client", lambda settings: _StubClient(payload), raising=True)
    monkeypatch.setattr("agents.ingest.parse_preferred_time_fr", _fixed_parse, raising=True)

    wa_stub = _StubWA()
    monkeypatch.setattr("agents.ingest.whatsapp_from_settings", lambda s: wa_stub, raising=True)

    from datetime import datetime, timedelta

    fixed = datetime.fromisoformat("2025-01-14T10:30:00+01:00")

    class _BusyFirstAvailLater:
        def is_available(self, start: datetime, duration_min: int = 30) -> bool:
            # Busy at the requested time, available +60min
            if start == fixed:
                return False
            return True

        def suggest_alternatives(self, start: datetime, *, duration_min: int = 30, count: int = 2):
            return [start + timedelta(minutes=60), start + timedelta(minutes=120)]

        def create_event(self, start: datetime, *, duration_min: int = 30, **kwargs):  # type: ignore[no-untyped-def]
            assert start != fixed
            return type("E", (), {"id": "evt-1"})()

    provider = _BusyFirstAvailLater()
    monkeypatch.setattr("agents.ingest.get_calendar_provider", lambda s: provider, raising=True)

    s = load_settings()
    msg1 = NormalizedMessage(
        message_id="wamid.PROP",
        timestamp="0",
        from_waid="+32000000002",
        to_phone_id="PHONE",
        type="text",
        text="Bonjour, mardi 10h30.",
        contact_name="Cara",
        raw={},
    )
    asyncio.run(handle_inbound_message(msg1, s))
    st = session_store.get("+32000000002")
    assert st.pending_alternatives and len(st.pending_alternatives) >= 1

    # Step 2: User replies "1" to choose the first alternative
    msg2 = NormalizedMessage(
        message_id="wamid.SEL",
        timestamp="0",
        from_waid="+32000000002",
        to_phone_id="PHONE",
        type="text",
        text="1",
        contact_name="Cara",
        raw={},
    )
    asyncio.run(handle_inbound_message(msg2, s))
    st2 = session_store.get("+32000000002")
    assert st2.event_id == "evt-1"
    assert st2.pending_alternatives is None
    assert wa_stub.sent and "Réservé" in wa_stub.sent[-1]["body"]
