from fastapi.testclient import TestClient

from app.main import create_app


def test_healthz_agents_configured_true_when_openai_key_set(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    app = create_app()
    client = TestClient(app)
    resp = client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["agents_configured"] is True


def test_healthz_agents_configured_false_when_no_key(monkeypatch):
    # Ensure no key is visible to the app, even if a local .env exists
    monkeypatch.setenv("OPENAI_API_KEY", "")
    app = create_app()
    client = TestClient(app)
    resp = client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["agents_configured"] is False
