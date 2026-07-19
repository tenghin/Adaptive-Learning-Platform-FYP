from datetime import datetime

from adaptive_learning.extensions import db


class StudentLearningProfile(db.Model):
    __tablename__ = "student_learning_profiles"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    preferred_learning_method = db.Column(db.String(30))

    total_results = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    average_quiz_score = db.Column(
        db.Float,
        nullable=False,
        default=0.0,
    )

    average_attempts = db.Column(
        db.Float,
        nullable=False,
        default=0.0,
    )

    material_success_rate = db.Column(
        db.Float,
        nullable=False,
        default=0.0,
    )

    summary_success_rate = db.Column(
        db.Float,
        nullable=False,
        default=0.0,
    )

    mindmap_success_rate = db.Column(
        db.Float,
        nullable=False,
        default=0.0,
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    student = db.relationship(
        "User",
        back_populates="learning_profile",
    )
