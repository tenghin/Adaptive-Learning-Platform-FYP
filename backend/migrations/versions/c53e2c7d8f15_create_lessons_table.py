"""Create lessons table

Revision ID: c53e2c7d8f15
Revises: b42d4c90e781
Create Date: 2026-07-06 12:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c53e2c7d8f15"
down_revision = "b42d4c90e781"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "course_id",
            "slug",
            name="uq_lessons_course_id_slug"
        )
    )
    op.create_index(
        op.f("ix_lessons_course_id"),
        "lessons",
        ["course_id"],
        unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_lessons_course_id"), table_name="lessons")
    op.drop_table("lessons")
