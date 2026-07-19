from datetime import datetime

from adaptive_learning.extensions import db


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    token_hash = db.Column(db.String(64), unique=True, nullable=False)

    expires_at = db.Column(db.DateTime, nullable=False)

    used_at = db.Column(db.DateTime)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        back_populates="password_reset_tokens"
    )

    def is_expired(self):
        return datetime.utcnow() >= self.expires_at

    def is_used(self):
        return self.used_at is not None
