from fastapi.testclient import TestClient

from terrasignal.api import app

client = TestClient(app)

def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_summary_is_labelled_demo() -> None:
    response = client.get("/api/v1/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "DEMO"
    assert payload["regions_monitored"] == 5
    assert payload["source_status"] == "No live satellite feeds connected"

def test_region_coordinates_and_risk_are_bounded() -> None:
    regions = client.get("/api/v1/regions").json()["items"]
    assert len(regions) == 5
    for region in regions:
        assert -22.5 <= region["lat"] <= -15.0
        assert 25.0 <= region["lon"] <= 33.5
        assert 0 <= region["risk"] <= 100

def test_alerts_require_review() -> None:
    alerts = client.get("/api/v1/alerts").json()["items"]
    assert len(alerts) == 3
    assert all(item["status"] in {"Needs review", "Under review"} for item in alerts)
