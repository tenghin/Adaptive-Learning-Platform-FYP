from datetime import datetime

from adaptive_learning.extensions import db


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)

    quiz_id = db.Column(
        db.Integer,
        db.ForeignKey("quizzes.id"),
        nullable=False,
        index=True
    )

    prompt = db.Column(db.Text, nullable=False)

    options = db.Column(db.JSON, nullable=False)

    correct_answer = db.Column(db.String(255), nullable=False)

    explanation = db.Column(db.Text)

    order_index = db.Column(
        db.Integer,
        nullable=False,
        default=1
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

    quiz = db.relationship(
        "Quiz",
        back_populates="questions"
    )
