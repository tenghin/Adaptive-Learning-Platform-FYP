from datetime import datetime

from adaptive_learning.extensions import db


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)

    lesson_id = db.Column(
        db.Integer,
        db.ForeignKey("lessons.id"),
        nullable=False,
        index=True
    )

    title = db.Column(db.String(150), nullable=False)

    description = db.Column(db.Text)

    pass_percentage = db.Column(
        db.Integer,
        nullable=False,
        default=70
    )

    is_published = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    lesson = db.relationship(
        "Lesson",
        back_populates="quizzes"
    )

    questions = db.relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan",
        order_by="Question.order_index.asc()"
    )

    attempts = db.relationship(
        "QuizAttempt",
        back_populates="quiz",
        cascade="all, delete-orphan"
    )
