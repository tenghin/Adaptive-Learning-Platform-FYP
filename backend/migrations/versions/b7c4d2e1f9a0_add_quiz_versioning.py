"""Add quiz versioning

Revision ID: b7c4d2e1f9a0
Revises: a4f8d1c3b2e7
Create Date: 2026-07-16 16:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b7c4d2e1f9a0"
down_revision = "a4f8d1c3b2e7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "quizzes",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.execute("UPDATE quizzes SET is_active = TRUE WHERE is_active IS NULL")
    op.execute("ALTER TABLE quizzes DROP CONSTRAINT IF EXISTS quizzes_lesson_id_key")
    op.execute("DROP INDEX IF EXISTS ix_quizzes_lesson_id")
    op.create_index(
        op.f("ix_quizzes_is_active"),
        "quizzes",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_quizzes_lesson_id"),
        "quizzes",
        ["lesson_id"],
        unique=False,
    )
    op.alter_column("quizzes", "is_active", server_default=None)


def downgrade():
    op.drop_index(op.f("ix_quizzes_is_active"), table_name="quizzes")
    op.drop_index(op.f("ix_quizzes_lesson_id"), table_name="quizzes")
    op.create_index(
        op.f("ix_quizzes_lesson_id"),
        "quizzes",
        ["lesson_id"],
        unique=True,
    )
    op.create_unique_constraint(
        "uq_quizzes_lesson_id",
        "quizzes",
        ["lesson_id"],
    )
    op.drop_column("quizzes", "is_active")
