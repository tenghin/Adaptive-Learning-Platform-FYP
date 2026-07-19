"""Add adaptive learning tables

Revision ID: a4f8d1c3b2e7
Revises: 5e6d36d577f2
Create Date: 2026-07-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "a4f8d1c3b2e7"
down_revision = "5e6d36d577f2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "student_learning_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("preferred_learning_method", sa.String(length=30), nullable=True),
        sa.Column("total_results", sa.Integer(), nullable=False),
        sa.Column("average_quiz_score", sa.Float(), nullable=False),
        sa.Column("average_attempts", sa.Float(), nullable=False),
        sa.Column("material_success_rate", sa.Float(), nullable=False),
        sa.Column("summary_success_rate", sa.Float(), nullable=False),
        sa.Column("mindmap_success_rate", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id"),
    )
    op.create_index(
        op.f("ix_student_learning_profiles_student_id"),
        "student_learning_profiles",
        ["student_id"],
        unique=True,
    )

    op.create_table(
        "student_learning_method_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("learning_method", sa.String(length=30), nullable=False),
        sa.Column("quiz_attempt_id", sa.Integer(), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("improvement", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"]),
        sa.ForeignKeyConstraint(["quiz_attempt_id"], ["quiz_attempts.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("quiz_attempt_id"),
    )
    op.create_index(
        op.f("ix_student_learning_method_results_lesson_id"),
        "student_learning_method_results",
        ["lesson_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_student_learning_method_results_quiz_attempt_id"),
        "student_learning_method_results",
        ["quiz_attempt_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_student_learning_method_results_student_id"),
        "student_learning_method_results",
        ["student_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f("ix_student_learning_method_results_student_id"),
        table_name="student_learning_method_results",
    )
    op.drop_index(
        op.f("ix_student_learning_method_results_quiz_attempt_id"),
        table_name="student_learning_method_results",
    )
    op.drop_index(
        op.f("ix_student_learning_method_results_lesson_id"),
        table_name="student_learning_method_results",
    )
    op.drop_table("student_learning_method_results")

    op.drop_index(
        op.f("ix_student_learning_profiles_student_id"),
        table_name="student_learning_profiles",
    )
    op.drop_table("student_learning_profiles")
