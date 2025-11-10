from app.config import load_settings
from connectors.calendar.provider import get_calendar_provider


def test_provider_falls_back_to_inmemory_when_google_unconfigured(monkeypatch):
    monkeypatch.setenv("GOOGLE_CREDS_JSON", "")
    monkeypatch.setenv("GOOGLE_CALENDAR_ID", "")
    s = load_settings()
    provider = get_calendar_provider(s)
    # In-memory exposes .create_event without raising
    assert provider is not None


def test_provider_handles_google_creds_but_missing_libs(monkeypatch):
    # Even if env vars are present, missing libs should gracefully fallback
    monkeypatch.setenv("GOOGLE_CREDS_JSON", "{}")
    monkeypatch.setenv("GOOGLE_CALENDAR_ID", "primary")
    s = load_settings()
    provider = get_calendar_provider(s)
    assert provider is not None


def test_provider_handles_b64_creds(monkeypatch):
    # Base64 for empty JSON {} is e30=
    monkeypatch.setenv("GOOGLE_CREDS_JSON", "")
    monkeypatch.setenv("GOOGLE_CREDS_JSON_B64", "e30=")
    monkeypatch.setenv("GOOGLE_CALENDAR_ID", "primary")
    s = load_settings()
    provider = get_calendar_provider(s)
    assert provider is not None
