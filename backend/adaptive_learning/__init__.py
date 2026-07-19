from flask import Flask
from flask_cors import CORS

from config import Config
from adaptive_learning.extensions import db, jwt, migrate
from adaptive_learning.routes.ai import ai_bp
from adaptive_learning.routes.auth import auth_bp
from adaptive_learning.routes.course import course_bp
from adaptive_learning.routes.lesson import lesson_bp
from adaptive_learning.routes.progress import progress_bp
from adaptive_learning.routes.quiz import quiz_bp
from adaptive_learning.utils.responses import error_response, success_response
from adaptive_learning.routes.recommendation import recommendation_bp
from adaptive_learning.models.student_learning_activity import StudentLearningActivity
from adaptive_learning.models.student_learning_method_result import (
    StudentLearningMethodResult,
)
from adaptive_learning.models.student_learning_profile import (
    StudentLearningProfile,
)
from adaptive_learning.services import learning_activity_service
from adaptive_learning.routes.learning_activity import activity_bp

def register_jwt_handlers():
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return error_response(
            "Session expired. Please log in again.",
            401
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return error_response("Invalid authentication token", 422)

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return error_response("Authentication token is required", 401)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    import os

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    CORS(
        app,
        resources={r"/api/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True,
    )

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    register_jwt_handlers()

    from adaptive_learning.models import (
        Course,
        Lesson,
        LessonResource,
        PasswordResetToken,
        Progress,
        Question,
        Quiz,
        QuizAttempt,
        StudentLearningMethodResult,
        StudentLearningProfile,
        User,
    )

    @app.route("/")
    def home():
        return success_response(
            "Welcome to Adaptive Learning Platform API"
        )

    @app.route("/health")
    def health():
        return success_response(
            "Service is healthy",
            {
                "status": "healthy",
                "service": "Adaptive Learning Platform API"
            }
        )

    app.register_blueprint(auth_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(lesson_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(activity_bp)

    return app
