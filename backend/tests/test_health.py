from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_app_has_expected_routes():
    paths = {r.path for r in app.routes}  # type: ignore[attr-defined]
    assert "/health" in paths
    assert "/api/consult" in paths
    assert "/api/proactive" in paths
