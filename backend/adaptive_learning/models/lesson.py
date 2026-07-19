from datetime import datetime

from adaptive_learning.extensions import db


class Lesson(db.Model):
    __tablename__ = "lessons"
    __table_args__ = (
        db.UniqueConstraint(
            "course_id",
            "slug",
            name="uq_lessons_course_id_slug"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id"),
        nullable=False,
        index=True
    )

    title = db.Column(db.String(150), nullable=False)

    slug = db.Column(db.String(160), nullable=False)

    content = db.Column(db.Text, nullable=False)

    summary = db.Column(db.Text)

    order_index = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    estimated_minutes = db.Column(
        db.Integer,
        nullable=False,
        default=15
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

    course = db.relationship(
        "Course",
        back_populates="lessons"
    )

    progress_records = db.relationship(
        "Progress",
        back_populates="lesson",
        cascade="all, delete-orphan"
    )

    resources = db.relationship(
        "LessonResource",
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="LessonResource.created_at.desc()"
    )

    quizzes = db.relationship(
        "Quiz",
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="Quiz.created_at.desc()"
    )

    learning_method_results = db.relationship(
        "StudentLearningMethodResult",
        back_populates="lesson",
        cascade="all, delete-orphan"
    )

    @property
    def active_quiz(self):
        for quiz in self.quizzes:
            if quiz.is_active:
                return quiz
        return None
