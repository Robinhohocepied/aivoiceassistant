import asyncio
import json

import pytest

from app.config import load_settings
from agents.session import store as session_store
from connectors.whatsapp.types import NormalizedMessage
from agents.ingest import handle_inbound_message


class _StubResp:
    def __init__(self, text: str) -> None:
        self.output_text = text


class _StubClient:
    class _Responses:
        def __init__(self, payload: str, fail_on_response_format: bool = False, fail_on_temperature_once: bool = False) -> None:
            self._payload = payload
            self._fail = fail_on_response_format
            self._fail_temp_once = fail_on_temperature_once

        def create(self, **kwargs):  # type: ignore[no-untyped-def]
            if self._fail and "response_format" in kwargs:
                raise TypeError("create() got an unexpected keyword argument 'response_format'")
            if self._fail_temp_once and "temperature" in kwargs:
                # Simulate server BadRequest: unsupported temperature
                self._fail_temp_once = False
                raise Exception("Unsupported parameter: 'temperature' is not supported with this model.")
            return _StubResp(self._payload)

    def __init__(self, payload: str, fail_on_response_format: bool = False, fail_on_temperature_once: bool = False) -> None:
        self.responses = self._Responses(payload, fail_on_response_format, fail_on_temperature_once)


def test_ingest_merges_extraction_and_normalizes_time(monkeypatch):
    session_store.clear()
    # Pretend OpenAI is configured
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    # Stub the agents client to return a fixed JSON extraction
    payload = json.dumps({
        "name": "Alice",
        "reason": "Douleur dentaire",
        "preferred_time": "mardi 10h30",
    })
    monkeypatch.setattr("agents.ingest.create_agents_client", lambda settings: _StubClient(payload), raising=True)
    # Make normalization deterministic
    monkeypatch.setattr(
        "agents.ingest.parse_preferred_time_fr",
        lambda text: type("P", (), {"iso": "2025-01-14T10:30:00+01:00"})(),
        raising=True,
    )

    s = load_settings()
    msg = NormalizedMessage(
        message_id="wamid.ABC",
        timestamp="0",
        from_waid="+32471123456",
        to_phone_id="PHONE_ID",
        type="text",
        text="Bonjour, je m'appelle Alice. Mardi 10h30." ,
        contact_name="Alice",
        raw={},
    )

    asyncio.run(handle_inbound_message(msg, s))

    st = session_store.get("+32471123456")
    assert st.name == "Alice"
    assert st.reason == "Douleur dentaire"
    assert st.preferred_time == "mardi 10h30"
    assert st.preferred_time_iso == "2025-01-14T10:30:00+01:00"


def test_ingest_fallback_without_response_format_when_unsupported(monkeypatch):
    session_store.clear()
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    payload = json.dumps({"name": "Bob", "reason": None, "preferred_time": "demain matin"})
    # First call will raise TypeError if response_format is present; our code should retry without it.
    monkeypatch.setattr(
        "agents.ingest.create_agents_client",
        lambda settings: _StubClient(payload, fail_on_response_format=True),
        raising=True,
    )
    # Deterministic normalization
    monkeypatch.setattr(
        "agents.ingest.parse_preferred_time_fr",
        lambda text: type("P", (), {"iso": "2025-01-11T09:00:00+01:00"})(),
        raising=True,
    )
    s = load_settings()
    msg = NormalizedMessage(
        message_id="wamid.X",
        timestamp="0",
        from_waid="+32000000000",
        to_phone_id="PHONE",
        type="text",
        text="Salut, demain matin ça va.",
        contact_name="Bob",
        raw={},
    )
    asyncio.run(handle_inbound_message(msg, s))
    st = session_store.get("+32000000000")
    assert st.name == "Bob" or st.name is None  # extraction sets name only if present
    assert st.preferred_time == "demain matin"
    assert st.preferred_time_iso == "2025-01-11T09:00:00+01:00"


def test_ingest_fallback_without_temperature_when_unsupported(monkeypatch):
    session_store.clear()
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    payload = json.dumps({"name": None, "reason": "Check-up", "preferred_time": "mercredi soir"})
    monkeypatch.setattr(
        "agents.ingest.create_agents_client",
        lambda settings: _StubClient(payload, fail_on_response_format=False, fail_on_temperature_once=True),
        raising=True,
    )
    monkeypatch.setattr(
        "agents.ingest.parse_preferred_time_fr",
        lambda text: type("P", (), {"iso": "2025-01-15T18:00:00+01:00"})(),
        raising=True,
    )
    s = load_settings()
    msg = NormalizedMessage(
        message_id="wamid.Y",
        timestamp="0",
        from_waid="+32111111111",
        to_phone_id="PHONE",
        type="text",
        text="Bonsoir, mercredi soir c'est bien.",
        contact_name="",
        raw={},
    )
    asyncio.run(handle_inbound_message(msg, s))
    st = session_store.get("+32111111111")
    assert st.reason == "Check-up"
    assert st.preferred_time == "mercredi soir"
    assert st.preferred_time_iso == "2025-01-15T18:00:00+01:00"
