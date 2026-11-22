from fastapi import FastAPI, HTTPException, Query
from prometheus_client import make_asgi_app
from sqlalchemy import text

from .db import make_engine

app = FastAPI(
    title="StreamForge API",
    description="Operational analytics API for the StreamForge event platform.",
    version="0.1.0",
)
engine = make_engine()
app.mount("/metrics", make_asgi_app())


@app.get("/health", tags=["operations"])
def health() -> dict:
    return {"status": "ok", "service": "streamforge-api"}


@app.get("/ready", tags=["operations"])
def ready() -> dict:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ready", "database": "reachable"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc


@app.get("/v1/analytics/summary", tags=["analytics"])
def summary() -> dict:
    query = text("""
        SELECT COUNT(*) AS event_count, COALESCE(SUM(gross_value), 0) AS gross_value,
               COUNT(*) FILTER (WHERE is_anomaly) AS anomaly_count,
               COUNT(DISTINCT customer_id) AS unique_customers
        FROM order_events
    """)
    with engine.connect() as connection:
        row = connection.execute(query).mappings().one()
    return {
        key: float(value) if key == "gross_value" else int(value)
        for key, value in row.items()
    }


@app.get("/v1/events/recent", tags=["events"])
def recent_events(limit: int = Query(default=25, ge=1, le=250)) -> list[dict]:
    query = text("""
        SELECT event_id, order_id, customer_id, event_time, amount, currency, quantity,
               gross_value, is_anomaly, anomaly_reasons
        FROM order_events ORDER BY event_time DESC LIMIT :limit
    """)
    with engine.connect() as connection:
        rows = connection.execute(query, {"limit": limit}).mappings().all()
    return [dict(row) for row in rows]
