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
        def __init__(self, payload: str) -> None:
            self._payload = payload

        def create(self, **kwargs):  # type: ignore[no-untyped-def]
            return _StubResp(self._payload)

    def __init__(self, payload: str) -> None:
        self.responses = self._Responses(payload)


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
    monkeypatch.setattr(
        "agents.ingest.create_agents_client",
        lambda settings: _StubClient(payload),
        raising=True,
    )
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
