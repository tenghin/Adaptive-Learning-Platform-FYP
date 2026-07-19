import re
from datetime import datetime, timedelta

from flask import current_app
from flask_jwt_extended import create_access_token
from sqlalchemy import or_

from adaptive_learning.extensions import db
from adaptive_learning.models.password_reset_token import PasswordResetToken
from adaptive_learning.models.user import User
from adaptive_learning.services import adaptive_learning_service
from adaptive_learning.utils.tokens import generate_secure_token, hash_token


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


def _success(message, data=None, status_code=200):
    return {
        "success": True,
        "message": message,
        "data": data or {}
    }, status_code


def _failure(message, status_code=400):
    return {
        "success": False,
        "message": message
    }, status_code


def _required_fields(data, fields):
    missing_fields = []

    for field in fields:
        value = data.get(field)
        if value is None or not str(value).strip():
            missing_fields.append(field)

    return missing_fields


def _validate_email(email):
    return bool(email and EMAIL_PATTERN.match(email))


def _validate_password(password):
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        return (
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
        )
    return None


def _serialize_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "is_active": user.is_active,
        "last_login": (
            user.last_login.isoformat()
            if user.last_login
            else None
        ),
        "created_at": user.created_at.isoformat()
    }


def _find_user_by_identifier(identifier):
    return User.query.filter(
        or_(
            User.email == identifier.lower(),
            User.username == identifier
        )
    ).first()


def _clear_expired_lock(user):
    if user.locked_until and user.locked_until <= datetime.utcnow():
        user.locked_until = None
        user.failed_login_attempts = 0


def _record_failed_login(user):
    max_attempts = current_app.config["MAX_FAILED_LOGIN_ATTEMPTS"]
    lock_minutes = current_app.config["ACCOUNT_LOCK_MINUTES"]

    user.failed_login_attempts += 1

    if user.failed_login_attempts >= max_attempts:
        user.locked_until = datetime.utcnow() + timedelta(
            minutes=lock_minutes
        )

    db.session.commit()


def _record_successful_login(user):
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    db.session.commit()


def register(data):
    data = data or {}
    required = [
        "username",
        "email",
        "password",
        "first_name",
        "last_name"
    ]
    missing_fields = _required_fields(data, required)

    if missing_fields:
        return _failure(
            f"Missing required fields: {', '.join(missing_fields)}"
        )

    username = data["username"].strip()
    email = data["email"].strip().lower()
    password = data["password"]
    first_name = data["first_name"].strip()
    last_name = data["last_name"].strip()

    if not _validate_email(email):
        return _failure("A valid email address is required")

    password_error = _validate_password(password)
    if password_error:
        return _failure(password_error)

    if User.query.filter_by(username=username).first():
        return _failure("Username already exists", 409)

    if User.query.filter_by(email=email).first():
        return _failure("Email already exists", 409)

    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role="student"
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return _success(
        "User registered successfully",
        {"user": _serialize_user(user)},
        201
    )


def login(data):
    data = data or {}
    identifier = (
        data.get("identifier")
        or data.get("email")
        or data.get("username")
    )
    password = data.get("password")

    if not identifier or not password:
        return _failure(
            "Identifier and password are required",
            400
        )

    identifier = str(identifier).strip()
    user = _find_user_by_identifier(identifier)

    if not user:
        return _failure("Invalid username/email or password", 401)

    _clear_expired_lock(user)

    if not user.is_active:
        db.session.commit()
        return _failure("Account is inactive", 403)

    if user.locked_until:
        db.session.commit()
        return _failure(
            "Account is temporarily locked. Please try again later.",
            423
        )

    if not user.check_password(password):
        _record_failed_login(user)
        if user.locked_until:
            return _failure(
                "Account is temporarily locked after too many failed logins.",
                423
            )
        return _failure("Invalid username/email or password", 401)

    _record_successful_login(user)

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    return _success(
        "Login successful",
        {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in_minutes": int(
                current_app.config[
                    "JWT_ACCESS_TOKEN_EXPIRES"
                ].total_seconds() // 60
            ),
            "user": _serialize_user(user)
        }
    )


def get_profile(user_id):
    user = db.session.get(User, int(user_id))

    if not user:
        return _failure("User not found", 404)

    learning_profile = adaptive_learning_service.get_learning_profile(user.id)
    learning_analytics = adaptive_learning_service.get_learning_analytics(user.id)

    return _success(
        "Profile retrieved successfully",
        {
            "user": _serialize_user(user),
            "learning_profile": (
                adaptive_learning_service.serialize_learning_profile(
                    learning_profile
                )
            ),
            "learning_analytics": learning_analytics,
        }
    )


def change_password(user_id, data):
    data = data or {}
    missing_fields = _required_fields(
        data,
        ["current_password", "new_password"]
    )

    if missing_fields:
        return _failure(
            "Current password and new password are required"
        )

    user = db.session.get(User, int(user_id))

    if not user:
        return _failure("User not found", 404)

    if not user.check_password(data["current_password"]):
        return _failure("Current password is incorrect", 400)

    password_error = _validate_password(data["new_password"])
    if password_error:
        return _failure(password_error)

    user.set_password(data["new_password"])
    db.session.commit()

    return _success("Password changed successfully")


def forgot_password(data):
    data = data or {}
    email = str(data.get("email", "")).strip().lower()

    if not email:
        return _failure("Email is required")

    if not _validate_email(email):
        return _failure("A valid email address is required")

    user = User.query.filter_by(email=email).first()
    response_data = {}

    if user and user.is_active:
        reset_token = generate_secure_token()
        expires_at = datetime.utcnow() + timedelta(
            minutes=current_app.config["PASSWORD_RESET_TOKEN_MINUTES"]
        )

        password_reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=hash_token(reset_token),
            expires_at=expires_at
        )

        db.session.add(password_reset_token)
        db.session.commit()

        if current_app.config["RETURN_PASSWORD_RESET_TOKEN"]:
            response_data["reset_token"] = reset_token
            response_data["expires_at"] = expires_at.isoformat()
    else:
        db.session.rollback()

    return _success(
        "If the email exists, a password reset link has been generated.",
        response_data
    )


def reset_password(data):
    data = data or {}
    missing_fields = _required_fields(data, ["token", "new_password"])

    if missing_fields:
        return _failure("Reset token and new password are required")

    password_error = _validate_password(data["new_password"])
    if password_error:
        return _failure(password_error)

    token_hash = hash_token(data["token"])
    password_reset_token = PasswordResetToken.query.filter_by(
        token_hash=token_hash
    ).first()

    if (
        not password_reset_token
        or password_reset_token.is_used()
        or password_reset_token.is_expired()
    ):
        return _failure("Reset token is invalid or expired", 400)

    user = password_reset_token.user

    if not user or not user.is_active:
        return _failure("Reset token is invalid or expired", 400)

    user.set_password(data["new_password"])
    user.failed_login_attempts = 0
    user.locked_until = None
    password_reset_token.used_at = datetime.utcnow()
    db.session.commit()

    return _success("Password reset successfully")
