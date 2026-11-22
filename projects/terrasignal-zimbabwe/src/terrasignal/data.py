"""Illustrative demo fixtures; not real satellite detections or verified statistics."""

from datetime import datetime, timezone

REGIONS = [
    {"id": "hurungwe", "name": "Hurungwe", "province": "Mashonaland West", "lat": -16.45, "lon": 29.75, "risk": 78, "status": "priority", "signal": "Vegetation stress"},
    {"id": "mutasa", "name": "Mutasa", "province": "Manicaland", "lat": -18.55, "lon": 32.85, "risk": 64, "status": "watch", "signal": "Canopy change"},
    {"id": "gokwe", "name": "Gokwe", "province": "Midlands", "lat": -18.20, "lon": 28.95, "risk": 51, "status": "watch", "signal": "Dryness anomaly"},
    {"id": "chipinge", "name": "Chipinge", "province": "Manicaland", "lat": -20.55, "lon": 32.45, "risk": 36, "status": "stable", "signal": "Seasonal variation"},
    {"id": "binga", "name": "Binga", "province": "Matabeleland North", "lat": -17.60, "lon": 27.35, "risk": 71, "status": "priority", "signal": "Fire-weather watch"},
]

ALERTS = [
    {"id": "TS-ZW-001", "region": "Hurungwe", "type": "Vegetation stress", "severity": "High", "confidence": 0.82, "status": "Needs review", "detail": "Illustrative sustained vegetation-index decline scenario."},
    {"id": "TS-ZW-002", "region": "Binga", "type": "Fire-weather watch", "severity": "High", "confidence": 0.74, "status": "Needs review", "detail": "Illustrative seasonal dryness watch scenario."},
    {"id": "TS-ZW-003", "region": "Mutasa", "type": "Canopy change", "severity": "Medium", "confidence": 0.68, "status": "Under review", "detail": "Illustrative change signal requiring imagery and field validation."},
]

def summary_payload() -> dict:
    return {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "mode": "DEMO",
        "source_status": "No live satellite feeds connected",
        "regions_monitored": len(REGIONS),
        "priority_regions": sum(item["status"] == "priority" for item in REGIONS),
        "alerts_open": len(ALERTS),
        "regions": REGIONS,
    }
