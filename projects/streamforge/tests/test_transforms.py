from datetime import UTC, datetime
from uuid import uuid4

from streamforge.config import Settings
from streamforge.schemas import OrderEvent
from streamforge.transforms import enrich_event


def make_event(amount=100, quantity=2):
    return OrderEvent(
        event_id=uuid4(),
        order_id="ORD-1",
        customer_id="CUST-1",
        event_time=datetime.now(UTC),
        amount=amount,
        currency="EUR",
        quantity=quantity,
    )


def test_normal_order_not_flagged():
    result = enrich_event(make_event(), Settings())
    assert result["is_anomaly"] is False
    assert result["gross_value"] == 200


def test_large_amount_flagged():
    result = enrich_event(make_event(amount=6000), Settings())
    assert result["is_anomaly"] is True
    assert "amount_threshold_exceeded" in result["anomaly_reasons"]


def test_large_quantity_flagged():
    result = enrich_event(make_event(quantity=120), Settings())
    assert "quantity_threshold_exceeded" in result["anomaly_reasons"]
