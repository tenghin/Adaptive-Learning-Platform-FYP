from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from adaptive_learning.services import quiz_service

quiz_bp = Blueprint(
    "quizzes",
    __name__,
    url_prefix="/api"
)


def _json_response(service_result):
    payload, status_code = service_result
    return jsonify(payload), status_code


@quiz_bp.route("/lessons/<int:lesson_id>/quiz", methods=["GET"])
@jwt_required()
def get_lesson_quiz(lesson_id):
    return _json_response(
        quiz_service.get_lesson_quiz(
            lesson_id,
            get_jwt().get("role")
        )
    )


@quiz_bp.route("/lessons/<int:lesson_id>/quiz", methods=["POST"])
@jwt_required()
def create_lesson_quiz(lesson_id):
    return _json_response(
        quiz_service.create_lesson_quiz(
            lesson_id,
            request.get_json(silent=True),
            get_jwt().get("role")
        )
    )


@quiz_bp.route("/quizzes/<int:quiz_id>", methods=["GET"])
@jwt_required()
def get_quiz(quiz_id):
    return _json_response(
        quiz_service.get_quiz(
            quiz_id,
            get_jwt().get("role")
        )
    )


@quiz_bp.route("/quizzes/<int:quiz_id>", methods=["PUT"])
@jwt_required()
def update_quiz(quiz_id):
    return _json_response(
        quiz_service.update_quiz(
            quiz_id,
            request.get_json(silent=True),
            get_jwt().get("role")
        )
    )


@quiz_bp.route("/quizzes/<int:quiz_id>", methods=["DELETE"])
@jwt_required()
def delete_quiz(quiz_id):
    return _json_response(
        quiz_service.delete_quiz(
            quiz_id,
            get_jwt().get("role")
        )
    )


@quiz_bp.route("/quizzes/<int:quiz_id>/attempts", methods=["POST"])
@jwt_required()
def submit_quiz_attempt(quiz_id):
    return _json_response(
        quiz_service.submit_quiz_attempt(
            quiz_id,
            get_jwt_identity(),
            get_jwt().get("role"),
            request.get_json(silent=True)
        )
    )


@quiz_bp.route("/quizzes/<int:quiz_id>/attempts/me", methods=["GET"])
@jwt_required()
def get_my_quiz_attempts(quiz_id):
    return _json_response(
        quiz_service.get_my_quiz_attempts(
            quiz_id,
            get_jwt_identity(),
            get_jwt().get("role")
        )
    )


@quiz_bp.route("/quizzes/<int:quiz_id>/attempts", methods=["GET"])
@jwt_required()
def list_quiz_attempts(quiz_id):
    return _json_response(
        quiz_service.list_quiz_attempts(
            quiz_id,
            get_jwt().get("role")
        )
    )
