from fastapi.testclient import TestClient

from app.main import create_app


def test_healthz_returns_ok():
    app = create_app()
    client = TestClient(app)
    resp = client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "mediflow"
    assert "version" in data
    assert "env" in data
    assert "time" in data
    assert "agents_configured" in data and isinstance(data["agents_configured"], bool)
