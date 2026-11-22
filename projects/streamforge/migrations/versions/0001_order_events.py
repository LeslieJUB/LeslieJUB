"""Create initial order events table.

Revision ID: 0001_order_events
Revises:
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_order_events"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "order_events",
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", sa.Text(), nullable=False),
        sa.Column("customer_id", sa.Text(), nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("gross_value", sa.Numeric(18, 2), nullable=False),
        sa.Column("is_anomaly", sa.Boolean(), nullable=False),
        sa.Column("anomaly_reasons", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("event_id", name="pk_order_events"),
    )
    op.create_index("idx_events_time", "order_events", ["event_time"], unique=False)
    op.create_index(
        "idx_events_anomaly",
        "order_events",
        ["is_anomaly"],
        unique=False,
        postgresql_where=sa.text("is_anomaly = TRUE"),
    )


def downgrade() -> None:
    op.drop_index("idx_events_anomaly", table_name="order_events")
    op.drop_index("idx_events_time", table_name="order_events")
    op.drop_table("order_events")
