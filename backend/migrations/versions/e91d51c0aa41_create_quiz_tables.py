"""Create quiz tables

Revision ID: e91d51c0aa41
Revises: d8f14b6ab209
Create Date: 2026-07-06 13:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "e91d51c0aa41"
down_revision = "d8f14b6ab209"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "quizzes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("pass_percentage", sa.Integer(), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lesson_id")
    )
    op.create_index(
        op.f("ix_quizzes_lesson_id"),
        "quizzes",
        ["lesson_id"],
        unique=True
    )

    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("quiz_id", sa.Integer(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("correct_answer", sa.String(length=255), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"]),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(
        op.f("ix_questions_quiz_id"),
        "questions",
        ["quiz_id"],
        unique=False
    )

    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("quiz_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("answers", sa.JSON(), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("correct_answers", sa.Integer(), nullable=False),
        sa.Column("score_percentage", sa.Integer(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(
        op.f("ix_quiz_attempts_quiz_id"),
        "quiz_attempts",
        ["quiz_id"],
        unique=False
    )
    op.create_index(
        op.f("ix_quiz_attempts_user_id"),
        "quiz_attempts",
        ["user_id"],
        unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_quiz_attempts_user_id"), table_name="quiz_attempts")
    op.drop_index(op.f("ix_quiz_attempts_quiz_id"), table_name="quiz_attempts")
    op.drop_table("quiz_attempts")

    op.drop_index(op.f("ix_questions_quiz_id"), table_name="questions")
    op.drop_table("questions")

    op.drop_index(op.f("ix_quizzes_lesson_id"), table_name="quizzes")
    op.drop_table("quizzes")
