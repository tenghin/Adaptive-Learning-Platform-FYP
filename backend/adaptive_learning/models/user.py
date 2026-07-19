from datetime import datetime

from adaptive_learning.extensions import db
from adaptive_learning.utils.password import (
    hash_password,
    verify_password,
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    first_name = db.Column(db.String(50), nullable=False)

    last_name = db.Column(db.String(50), nullable=False)

    role = db.Column(
        db.String(20),
        nullable=False,
        default="student"
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    failed_login_attempts = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    locked_until = db.Column(db.DateTime)

    last_login = db.Column(db.DateTime)

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

    password_reset_tokens = db.relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    progress_records = db.relationship(
        "Progress",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    quiz_attempts = db.relationship(
        "QuizAttempt",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    learning_method_results = db.relationship(
        "StudentLearningMethodResult",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    learning_profile = db.relationship(
        "StudentLearningProfile",
        back_populates="student",
        cascade="all, delete-orphan",
        uselist=False
    )

    def set_password(self, password):
        self.password_hash = hash_password(password)

    def check_password(self, password):
        return verify_password(password, self.password_hash)
