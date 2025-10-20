import asyncio

from app.config import load_settings
from connectors.whatsapp.client import from_settings


def test_from_settings_none_without_env(monkeypatch):
    # Ensure both env vars are effectively empty (robust even if a .env exists)
    monkeypatch.setenv("WHATSAPP_TOKEN", "")
    monkeypatch.setenv("WHATSAPP_PHONE_ID", "")
    s = load_settings()
    client = from_settings(s)
    assert client is None


def test_from_settings_with_env_and_dry_run(monkeypatch):
    monkeypatch.setenv("WHATSAPP_TOKEN", "test-token")
    monkeypatch.setenv("WHATSAPP_PHONE_ID", "12345")
    monkeypatch.setenv("WHATSAPP_BASE_URL", "https://graph.facebook.com/v18.0")
    s = load_settings()
    client = from_settings(s)
    assert client is not None
    # messages_url should be constructed correctly
    assert client.messages_url.endswith("/12345/messages")
    # Dry run should not perform network I/O and return preview payload
    out = asyncio.run(client.send_text(to="+10000000000", body="Hello", dry_run=True))
    assert out.get("dry_run") is True
    payload = out.get("payload")
    assert payload["to"] == "10000000000"
    assert payload["type"] == "text"
    assert payload["text"]["body"] == "Hello"
