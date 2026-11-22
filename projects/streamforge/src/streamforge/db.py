from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from .config import get_settings

def make_engine() -> Engine:
    return create_engine(get_settings().database_url, pool_pre_ping=True)

def initialise_database(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS order_events (
                event_id UUID PRIMARY KEY, order_id TEXT NOT NULL, customer_id TEXT NOT NULL,
                event_time TIMESTAMPTZ NOT NULL, ingested_at TIMESTAMPTZ NOT NULL,
                amount NUMERIC(18,2) NOT NULL, currency CHAR(3) NOT NULL,
                quantity INTEGER NOT NULL, gross_value NUMERIC(18,2) NOT NULL,
                is_anomaly BOOLEAN NOT NULL, anomaly_reasons JSONB NOT NULL,
                source TEXT NOT NULL, payload JSONB NOT NULL
            )
        """))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_events_time ON order_events (event_time DESC)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS idx_events_anomaly ON order_events (is_anomaly) WHERE is_anomaly = TRUE"))
