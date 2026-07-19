"""Create courses table

Revision ID: b42d4c90e781
Revises: a9c3f7d21b64
Create Date: 2026-07-06 12:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b42d4c90e781"
down_revision = "a9c3f7d21b64"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("difficulty_level", sa.String(length=20), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug")
    )


def downgrade():
    op.drop_table("courses")
