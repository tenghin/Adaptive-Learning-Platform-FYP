import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 30))
    )

    MAX_FAILED_LOGIN_ATTEMPTS = int(
        os.getenv("MAX_FAILED_LOGIN_ATTEMPTS", 5)
    )
    ACCOUNT_LOCK_MINUTES = int(os.getenv("ACCOUNT_LOCK_MINUTES", 15))
    PASSWORD_RESET_TOKEN_MINUTES = int(
        os.getenv("PASSWORD_RESET_TOKEN_MINUTES", 30)
    )
    RETURN_PASSWORD_RESET_TOKEN = (
        os.getenv("RETURN_PASSWORD_RESET_TOKEN", "true").lower() == "true"
    )

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__),
        "uploads"
    )