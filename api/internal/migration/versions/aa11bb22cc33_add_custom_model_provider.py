"""add custom model provider table

Revision ID: aa11bb22cc33
Revises: f9a1b2c3d4e5
Create Date: 2026-10-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "aa11bb22cc33"
down_revision = "f9a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "custom_model_provider",
        sa.Column("id", sa.UUID(), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(length=255), nullable=False, server_default=sa.text("''::character varying")),
        sa.Column("label", sa.String(length=255), nullable=False, server_default=sa.text("''::character varying")),
        sa.Column("api_key", sa.Text(), nullable=False, server_default=sa.text("''::text")),
        sa.Column("base_url", sa.String(length=1024), nullable=False, server_default=sa.text("''::character varying")),
        sa.Column("model_type", sa.String(length=64), nullable=False, server_default=sa.text("'chat'::character varying")),
        sa.Column("models", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("features", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[\"tool_call\"]'::jsonb")),
        sa.Column("context_window", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("max_output_tokens", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(0)"), server_onupdate=sa.text("CURRENT_TIMESTAMP(0)")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(0)")),
        sa.PrimaryKeyConstraint("id", name="pk_custom_model_provider_id"),
    )
    op.create_index("custom_model_provider_name_idx", "custom_model_provider", ["name"])


def downgrade():
    op.drop_index("custom_model_provider_name_idx", table_name="custom_model_provider")
    op.drop_table("custom_model_provider")
