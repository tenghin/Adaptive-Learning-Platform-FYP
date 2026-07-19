from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from adaptive_learning.services import recommendation_service


recommendation_bp = Blueprint(
    "recommendations",
    __name__,
    url_prefix="/api"
)


def _json_response(service_result):
    payload, status_code = service_result
    return jsonify(payload), status_code


@recommendation_bp.route(
    "/lessons/<int:lesson_id>/recommendation",
    methods=["GET"]
)
@jwt_required()
def get_lesson_recommendation(lesson_id):
    return _json_response(
        recommendation_service.get_lesson_recommendation(
            lesson_id,
            get_jwt_identity(),
            get_jwt().get("role"),
        )
    )

@recommendation_bp.route(
    "/lessons/<int:lesson_id>/recommendation/advance",
    methods=["POST"]
)
@jwt_required()
def advance_learning_stage(lesson_id):
    return _json_response(
        recommendation_service.advance_learning_stage(
            lesson_id,
            get_jwt_identity(),
            get_jwt().get("role"),
        )
    )
