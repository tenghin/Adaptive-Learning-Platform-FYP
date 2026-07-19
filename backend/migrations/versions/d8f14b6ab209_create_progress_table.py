"""Create progress table

Revision ID: d8f14b6ab209
Revises: c53e2c7d8f15
Create Date: 2026-07-06 13:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "d8f14b6ab209"
down_revision = "c53e2c7d8f15"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("completion_percentage", sa.Integer(), nullable=False),
        sa.Column("last_accessed_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "lesson_id",
            name="uq_progress_user_id_lesson_id"
        )
    )
    op.create_index(
        op.f("ix_progress_lesson_id"),
        "progress",
        ["lesson_id"],
        unique=False
    )
    op.create_index(
        op.f("ix_progress_user_id"),
        "progress",
        ["user_id"],
        unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_progress_user_id"), table_name="progress")
    op.drop_index(op.f("ix_progress_lesson_id"), table_name="progress")
    op.drop_table("progress")
