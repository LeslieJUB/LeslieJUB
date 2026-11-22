from datetime import date

from fastapi.testclient import TestClient

from terrasignal.api import app
from terrasignal.data import ProviderUnavailable

client = TestClient(app)


def test_health_reports_live_upstream_mode() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["data_mode"] == "live-upstream"


def test_invalid_date_range_is_rejected() -> None:
    response = client.get(
        "/api/v1/sentinel/scenes",
        params={"start": "2026-11-20", "end": "2026-11-01"},
    )
    assert response.status_code == 422


def test_firms_missing_key_returns_configuration_error(monkeypatch) -> None:
    monkeypatch.delenv("NASA_FIRMS_MAP_KEY", raising=False)
    response = client.get("/api/v1/fires")
    assert response.status_code == 503
    assert "NASA_FIRMS_MAP_KEY" in response.json()["detail"]


def test_sentinel_provider_failure_is_not_hidden(monkeypatch) -> None:
    async def fail(*args, **kwargs):
        raise ProviderUnavailable("upstream unavailable")

    monkeypatch.setattr("terrasignal.api.sentinel2_catalogue", fail)
    response = client.get("/api/v1/sentinel/scenes")
    assert response.status_code == 503
    assert response.json()["detail"] == "upstream unavailable"
