from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, jwt_required

from adaptive_learning.ai import ai_service

ai_bp = Blueprint(
    "ai",
    __name__,
    url_prefix="/api"
)


def _json_response(service_result):
    payload, status_code = service_result
    return jsonify(payload), status_code


@ai_bp.route("/lessons/<int:lesson_id>/ai/summary", methods=["POST"])
@jwt_required()
def generate_lesson_summary(lesson_id):
    return _json_response(
        ai_service.generate_lesson_summary(
            lesson_id,
            get_jwt().get("role")
        )
    )


@ai_bp.route("/lessons/<int:lesson_id>/ai/knowledge-graph", methods=["POST"])
@jwt_required()
def generate_lesson_knowledge_graph(lesson_id):
    return _json_response(
        ai_service.generate_lesson_knowledge_graph(
            lesson_id,
            get_jwt().get("role")
        )
    )

from adaptive_learning.services import quiz_service

@ai_bp.route("/lessons/<int:lesson_id>/ai/quiz", methods=["POST"])
@jwt_required()
def generate_lesson_quiz(lesson_id):
    return _json_response(
        quiz_service.create_lesson_quiz(
            lesson_id,
            None,
            get_jwt().get("role")
        )
    )