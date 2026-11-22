from datetime import UTC, datetime

from .config import Settings
from .schemas import OrderEvent


def enrich_event(event: OrderEvent, settings: Settings) -> dict:
    now = datetime.now(UTC)
    age_seconds = max(0.0, (now - event.event_time).total_seconds())
    reasons = []
    if event.amount > settings.anomaly_amount_threshold:
        reasons.append("amount_threshold_exceeded")
    if event.quantity > settings.anomaly_quantity_threshold:
        reasons.append("quantity_threshold_exceeded")
    return {
        **event.model_dump(mode="json"),
        "ingested_at": now.isoformat(),
        "event_age_seconds": round(age_seconds, 3),
        "is_anomaly": bool(reasons),
        "anomaly_reasons": reasons,
        "gross_value": round(event.amount * event.quantity, 2),
    }
