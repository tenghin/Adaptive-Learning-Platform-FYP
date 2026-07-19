from datetime import datetime

from adaptive_learning.extensions import db


class Progress(db.Model):
    __tablename__ = "progress"
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "lesson_id",
            name="uq_progress_user_id_lesson_id"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    lesson_id = db.Column(
        db.Integer,
        db.ForeignKey("lessons.id"),
        nullable=False,
        index=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="not_started"
    )

    completion_percentage = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    current_learning_stage = db.Column(
        db.String(30),
        nullable=False,
        default="lesson"
    )

    last_accessed_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    completed_at = db.Column(db.DateTime)

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

    user = db.relationship(
        "User",
        back_populates="progress_records"
    )

    lesson = db.relationship(
        "Lesson",
        back_populates="progress_records"
    )
