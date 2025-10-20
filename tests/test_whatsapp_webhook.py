from fastapi.testclient import TestClient

from app.main import create_app
from connectors.whatsapp.store import store


def test_whatsapp_verify_success(monkeypatch):
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "secret-token")
    app = create_app()
    client = TestClient(app)
    resp = client.get(
        "/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "secret-token",
            "hub.challenge": "12345",
        },
    )
    assert resp.status_code == 200
    assert resp.text == "12345"


def test_whatsapp_verify_forbidden(monkeypatch):
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "secret-token")
    app = create_app()
    client = TestClient(app)
    resp = client.get(
        "/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong",
            "hub.challenge": "12345",
        },
    )
    assert resp.status_code == 403


def test_whatsapp_inbound_text_message(monkeypatch):
    store.clear()
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
    assert resp.text == "EVENT_RECEIVED"
    messages = store.all()
    assert len(messages) == 1
    m = messages[0]
    assert m.from_waid == "+32471123456"
    assert m.to_phone_id == "PHONE_ID"
    assert m.type == "text"
    assert m.text == "Bonjour"
    assert m.contact_name == "Alice"

