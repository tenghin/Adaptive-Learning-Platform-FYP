from datetime import datetime

from adaptive_learning.extensions import db


class StudentLearningActivity(db.Model):
    __tablename__ = "student_learning_activities"

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

    activity_type = db.Column(
        db.String(50),
        nullable=False,
    )

    duration_seconds = db.Column(
        db.Integer,
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    student = db.relationship("User")

    lesson = db.relationship("Lesson")