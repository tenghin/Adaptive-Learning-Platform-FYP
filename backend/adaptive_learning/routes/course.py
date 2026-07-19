from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from adaptive_learning.services import course_service

course_bp = Blueprint(
    "courses",
    __name__,
    url_prefix="/api/courses"
)


def _json_response(service_result):
    payload, status_code = service_result
    return jsonify(payload), status_code


@course_bp.route("", methods=["GET"])
@jwt_required()
def list_courses():
    return _json_response(
        course_service.list_courses(get_jwt().get("role"))
    )


@course_bp.route("/<int:course_id>", methods=["GET"])
@jwt_required()
def get_course(course_id):
    return _json_response(
        course_service.get_course(course_id, get_jwt().get("role"))
    )


@course_bp.route("", methods=["POST"])
@jwt_required()
def create_course():
    return _json_response(
        course_service.create_course(
            request.get_json(silent=True),
            get_jwt().get("role")
        )
    )


@course_bp.route("/<int:course_id>", methods=["PUT"])
@jwt_required()
def update_course(course_id):
    return _json_response(
        course_service.update_course(
            course_id,
            request.get_json(silent=True),
            get_jwt().get("role")
        )
    )


@course_bp.route("/<int:course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):
    return _json_response(
        course_service.delete_course(course_id, get_jwt().get("role"))
    )
