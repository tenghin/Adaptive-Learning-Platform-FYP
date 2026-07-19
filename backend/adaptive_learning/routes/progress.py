from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from adaptive_learning.services import progress_service

progress_bp = Blueprint(
    "progress",
    __name__,
    url_prefix="/api/progress"
)


def _json_response(service_result):
    payload, status_code = service_result
    return jsonify(payload), status_code


@progress_bp.route("", methods=["GET"])
@jwt_required()
def get_progress_overview():
    return _json_response(
        progress_service.get_progress_overview(
            get_jwt_identity(),
            get_jwt().get("role")
        )
    )


@progress_bp.route("/courses/<int:course_id>", methods=["GET"])
@jwt_required()
def get_course_progress(course_id):
    return _json_response(
        progress_service.get_course_progress(
            get_jwt_identity(),
            course_id,
            get_jwt().get("role")
        )
    )

@progress_bp.route("/lessons/<int:lesson_id>", methods=["GET"])
@jwt_required()
def get_lesson_progress(lesson_id):
    return _json_response(
        progress_service.get_lesson_progress(
            get_jwt_identity(),
            lesson_id,
            get_jwt().get("role")
        )
    )

@progress_bp.route("/lessons/<int:lesson_id>", methods=["PUT"])
@jwt_required()
def update_lesson_progress(lesson_id):
    return _json_response(
        progress_service.update_lesson_progress(
            get_jwt_identity(),
            lesson_id,
            get_jwt().get("role"),
            request.get_json(silent=True)
        )
    )

@progress_bp.route("/lessons/<int:lesson_id>", methods=["DELETE"])
@jwt_required()
def reset_lesson_progress(lesson_id):
    return _json_response(
        progress_service.reset_lesson_progress(
            get_jwt_identity(),
            lesson_id
        )
    )