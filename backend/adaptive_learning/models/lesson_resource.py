from datetime import datetime

from adaptive_learning.extensions import db


class LessonResource(db.Model):
    __tablename__ = "lesson_resources"

    id = db.Column(db.Integer, primary_key=True)

    lesson_id = db.Column(
        db.Integer,
        db.ForeignKey("lessons.id"),
        nullable=False,
        index=True
    )

    title = db.Column(db.String(150), nullable=False)

    resource_type = db.Column(
        db.String(50),
        nullable=False,
        default="document"
    )

    content = db.Column(db.Text, nullable=False)

    file_name = db.Column(db.String(255))

    file_path = db.Column(db.String(500))

    mime_type = db.Column(db.String(100))

    is_generated = db.Column(
        db.Boolean,
        nullable=False,
        default=False
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

    lesson = db.relationship(
        "Lesson",
        back_populates="resources"
    )