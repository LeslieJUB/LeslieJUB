from fastapi.testclient import TestClient

from streamforge import api


class FakeConnection:
    def execute(self, statement):
        return None


class FakeEngine:
    def connect(self):
        class Context:
            def __enter__(self):
                return FakeConnection()

            def __exit__(self, *args):
                return False

        return Context()


def test_health_endpoint(monkeypatch):
    monkeypatch.setattr(api, "initialise_database", lambda engine: None)
    monkeypatch.setattr(api, "engine", FakeEngine())
    with TestClient(api.app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readiness_endpoint_checks_database(monkeypatch):
    monkeypatch.setattr(api, "initialise_database", lambda engine: None)
    monkeypatch.setattr(api, "engine", FakeEngine())
    with TestClient(api.app) as client:
        response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "reachable"
