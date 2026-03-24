"""initial tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-03-24
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


status_state = sa.Enum("open", "closed", "paused", "likely_closed", name="statusstate", native_enum=False)
status_channel = sa.Enum("whatsapp", "telegram", "missed_call", "auto", "ml", name="statuschannel", native_enum=False)
plan_type = sa.Enum("free", "basic", name="plantype", native_enum=False)
payment_status = sa.Enum("active", "overdue", "cancelled", name="paymentstatus", native_enum=False)


def upgrade():
    op.create_table(
        "shops",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("legal_name", sa.String(length=200), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("owner_phone", sa.String(length=20), nullable=False),
        sa.Column("whatsapp_number", sa.String(length=20), nullable=True),
        sa.Column("telegram_handle", sa.String(length=50), nullable=True),
        sa.Column("upi_handle", sa.String(length=120), nullable=True),
        sa.Column("address", sa.String(length=300), nullable=True),
        sa.Column("pincode", sa.String(length=6), nullable=False),
        sa.Column("geo_lat", sa.Float(), nullable=True),
        sa.Column("geo_lng", sa.Float(), nullable=True),
        sa.Column("status_default_schedule", sa.JSON(), nullable=True),
        sa.Column("languages", sa.JSON(), nullable=True),
        sa.UniqueConstraint("owner_phone", name="uq_shops_owner_phone"),
    )
    op.create_index("idx_shops_pincode", "shops", ["pincode"])
    op.create_index("idx_shops_display_name", "shops", ["display_name"])

    op.create_table(
        "status_events",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("shop_id", sa.Uuid(), sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("state", status_state, nullable=False),
        sa.Column("channel", status_channel, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.String(length=50), nullable=True),
    )
    op.create_index("idx_status_events_shop", "status_events", ["shop_id", "created_at"])

    op.create_table(
        "service_items",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("shop_id", sa.Uuid(), sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("price_min", sa.Numeric(10, 2), nullable=True),
        sa.Column("price_max", sa.Numeric(10, 2), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("duration_mins", sa.Integer(), nullable=True),
        sa.Column("supports_home_visit", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("idx_service_items_shop", "service_items", ["shop_id"])

    op.create_table(
        "user_checks",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("shop_id", sa.Uuid(), sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_geo_lat", sa.Numeric(9, 6), nullable=True),
        sa.Column("user_geo_lng", sa.Numeric(9, 6), nullable=True),
        sa.Column("result_state", sa.String(length=30), nullable=False),
        sa.Column("fallback_clicked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_user_checks_shop", "user_checks", ["shop_id", "created_at"])

    op.create_table(
        "fallback_shops",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("shop_id", sa.Uuid(), sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alt_shop_id", sa.Uuid(), sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("distance_km", sa.Numeric(6, 3), nullable=True),
        sa.Column("score", sa.Numeric(5, 2), nullable=True),
        sa.Column("note", sa.String(length=200), nullable=True),
    )
    op.create_index("idx_fallback_shop", "fallback_shops", ["shop_id"])

    op.create_table(
        "payment_plans",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("shop_id", sa.Uuid(), sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan", plan_type, nullable=False, server_default="free"),
        sa.Column("next_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payment_link", sa.String(length=300), nullable=True),
        sa.Column("status", payment_status, nullable=False, server_default="active"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_payment_shop", "payment_plans", ["shop_id"])

    op.create_table(
        "reopen_subscriptions",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("shop_id", sa.Uuid(), sa.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_contact", sa.String(length=120), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notified_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_reopen_shop", "reopen_subscriptions", ["shop_id"])

    op.create_table(
        "bot_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("contact", sa.String(length=120), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("step", sa.String(length=50), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("contact", name="uq_bot_sessions_contact"),
    )


def downgrade():
    op.drop_table("bot_sessions")

    op.drop_index("idx_reopen_shop", table_name="reopen_subscriptions")
    op.drop_table("reopen_subscriptions")

    op.drop_index("idx_payment_shop", table_name="payment_plans")
    op.drop_table("payment_plans")

    op.drop_index("idx_fallback_shop", table_name="fallback_shops")
    op.drop_table("fallback_shops")

    op.drop_index("idx_user_checks_shop", table_name="user_checks")
    op.drop_table("user_checks")

    op.drop_index("idx_service_items_shop", table_name="service_items")
    op.drop_table("service_items")

    op.drop_index("idx_status_events_shop", table_name="status_events")
    op.drop_table("status_events")

    op.drop_index("idx_shops_display_name", table_name="shops")
    op.drop_index("idx_shops_pincode", table_name="shops")
    op.drop_table("shops")
