import json
from sqlalchemy import text
from sqlalchemy.engine import Engine

UPSERT_SQL = text("""
INSERT INTO order_events (
 event_id, order_id, customer_id, event_time, ingested_at, amount, currency,
 quantity, gross_value, is_anomaly, anomaly_reasons, source, payload
) VALUES (
 :event_id, :order_id, :customer_id, :event_time, :ingested_at, :amount, :currency,
 :quantity, :gross_value, :is_anomaly, CAST(:anomaly_reasons AS jsonb), :source, CAST(:payload AS jsonb)
)
ON CONFLICT (event_id) DO UPDATE SET
 ingested_at = EXCLUDED.ingested_at, is_anomaly = EXCLUDED.is_anomaly,
 anomaly_reasons = EXCLUDED.anomaly_reasons, payload = EXCLUDED.payload
""")

def persist_batch(engine: Engine, records: list[dict]) -> None:
    if not records:
        return
    params = [{
        **row,
        "anomaly_reasons": json.dumps(row["anomaly_reasons"]),
        "payload": json.dumps(row),
    } for row in records]
    with engine.begin() as connection:
        connection.execute(UPSERT_SQL, params)
