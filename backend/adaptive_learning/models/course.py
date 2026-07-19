from datetime import datetime

from adaptive_learning.extensions import db


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)

    slug = db.Column(db.String(160), unique=True, nullable=False)

    description = db.Column(db.Text, nullable=False)

    difficulty_level = db.Column(
        db.String(20),
        nullable=False,
        default="beginner"
    )

    estimated_minutes = db.Column(
        db.Integer,
        nullable=False,
        default=60
    )

    is_published = db.Column(
        db.Boolean,
        nullable=False,
        default=True
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

    lessons = db.relationship(
        "Lesson",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Lesson.order_index.asc()"
    )
