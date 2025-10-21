import asyncio
from fastapi.testclient import TestClient

from app.main import create_app


def test_autoreply_dry_run(monkeypatch):
    # Enable autoreply and dry-run; fake WhatsApp creds
    monkeypatch.setenv("WHATSAPP_AUTOREPLY", "true")
    monkeypatch.setenv("WHATSAPP_DRY_RUN", "true")
    monkeypatch.setenv("WHATSAPP_TOKEN", "x-token")
    monkeypatch.setenv("WHATSAPP_PHONE_ID", "PHONE_ID")
    # No OPENAI_API_KEY on purpose -> fallback reply

    # Capture send_text calls
    calls = {}

    async def fake_send_text(self, to: str, body: str, dry_run: bool = False):  # type: ignore[no-redef]
        calls["to"] = to
        calls["body"] = body
        calls["dry_run"] = dry_run
        return {"dry_run": dry_run, "to": to, "body": body}

    import connectors.whatsapp.client as wa_client

    monkeypatch.setattr(wa_client.WhatsAppClient, "send_text", fake_send_text)

    app = create_app()
    client = TestClient(app)

    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "metadata": {"phone_number_id": "PHONE_ID"},
                            "contacts": [
                                {"profile": {"name": "Alice"}, "wa_id": "+32471123456"}
                            ],
                            "messages": [
                                {
                                    "from": "+32471123456",
                                    "id": "wamid.ABC",
                                    "timestamp": "1690000000",
                                    "type": "text",
                                    "text": {"body": "Bonjour"},
                                }
                            ],
                        }
                    }
                ]
            }
        ]
    }

    resp = client.post("/webhooks/whatsapp", json=payload)
    assert resp.status_code == 200
    # Ensure our fake sender was called with expected args
    assert calls["to"] == "+32471123456"
    assert isinstance(calls["body"], str) and len(calls["body"]) > 0
    assert calls["dry_run"] is True

