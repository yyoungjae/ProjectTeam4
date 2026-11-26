from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_not_found_uses_error_format():
    with TestClient(app) as client:
        res = client.get("/api/does-not-exist")
    assert res.status_code == 404
    assert res.json()["code"] == "NOT_FOUND"
