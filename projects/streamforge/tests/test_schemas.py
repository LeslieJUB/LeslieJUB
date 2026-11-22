from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from streamforge.schemas import OrderEvent


def valid_event(**overrides):
    payload = {
        "event_id": str(uuid4()),
        "order_id": "ORD-1",
        "customer_id": "CUST-1",
        "event_time": datetime.now(UTC).isoformat(),
        "amount": 12.5,
        "currency": "EUR",
        "quantity": 2,
    }
    return {**payload, **overrides}


def test_valid_order_event_parses():
    event = OrderEvent.model_validate(valid_event())
    assert event.currency == "EUR"
    assert event.quantity == 2


def test_negative_amount_is_rejected():
    with pytest.raises(ValidationError):
        OrderEvent.model_validate(valid_event(amount=-1))


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValidationError):
        OrderEvent.model_validate(valid_event(event_time="2026-01-01T12:00:00"))


def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError):
        OrderEvent.model_validate(valid_event(unexpected="not-allowed"))
