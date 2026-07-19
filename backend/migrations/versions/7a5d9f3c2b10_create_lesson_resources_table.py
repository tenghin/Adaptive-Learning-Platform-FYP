"""Create lesson resources table

Revision ID: 7a5d9f3c2b10
Revises: e91d51c0aa41
Create Date: 2026-07-06 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "7a5d9f3c2b10"
down_revision = "e91d51c0aa41"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "lesson_resources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("resource_type", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("mime_type", sa.String(length=100), nullable=True),
        sa.Column("is_generated", sa.Boolean(), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"]),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(
        op.f("ix_lesson_resources_lesson_id"),
        "lesson_resources",
        ["lesson_id"],
        unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_lesson_resources_lesson_id"), table_name="lesson_resources")
    op.drop_table("lesson_resources")