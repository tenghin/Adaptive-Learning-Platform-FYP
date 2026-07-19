"""Create password reset tokens table

Revision ID: a9c3f7d21b64
Revises: 4e875b76c455
Create Date: 2026-07-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "a9c3f7d21b64"
down_revision = "4e875b76c455"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash")
    )
    op.create_index(
        op.f("ix_password_reset_tokens_user_id"),
        "password_reset_tokens",
        ["user_id"],
        unique=False
    )


def downgrade():
    op.drop_index(
        op.f("ix_password_reset_tokens_user_id"),
        table_name="password_reset_tokens"
    )
    op.drop_table("password_reset_tokens")
