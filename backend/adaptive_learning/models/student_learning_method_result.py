from datetime import datetime

from adaptive_learning.extensions import db


class StudentLearningMethodResult(db.Model):
    __tablename__ = "student_learning_method_results"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    lesson_id = db.Column(
        db.Integer,
        db.ForeignKey("lessons.id"),
        nullable=False,
        index=True,
    )

    learning_method = db.Column(
        db.String(30),
        nullable=False,
    )

    quiz_attempt_id = db.Column(
        db.Integer,
        db.ForeignKey("quiz_attempts.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    attempt_number = db.Column(
        db.Integer,
        nullable=False,
    )

    score = db.Column(
        db.Integer,
        nullable=False,
    )

    passed = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    improvement = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    student = db.relationship(
        "User",
        back_populates="learning_method_results",
    )

    lesson = db.relationship(
        "Lesson",
        back_populates="learning_method_results",
    )

    quiz_attempt = db.relationship(
        "QuizAttempt",
        back_populates="learning_method_result",
    )
