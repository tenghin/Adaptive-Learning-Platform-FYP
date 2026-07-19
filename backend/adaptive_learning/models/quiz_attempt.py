from datetime import datetime

from adaptive_learning.extensions import db


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"

    id = db.Column(db.Integer, primary_key=True)

    quiz_id = db.Column(
        db.Integer,
        db.ForeignKey("quizzes.id"),
        nullable=False,
        index=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    answers = db.Column(db.JSON, nullable=False)

    total_questions = db.Column(db.Integer, nullable=False)

    correct_answers = db.Column(db.Integer, nullable=False)

    score_percentage = db.Column(db.Integer, nullable=False)

    passed = db.Column(db.Boolean, nullable=False, default=False)

    submitted_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    quiz = db.relationship(
        "Quiz",
        back_populates="attempts"
    )

    user = db.relationship(
        "User",
        back_populates="quiz_attempts"
    )

    learning_method_result = db.relationship(
        "StudentLearningMethodResult",
        back_populates="quiz_attempt",
        uselist=False,
        cascade="all, delete-orphan"
    )
