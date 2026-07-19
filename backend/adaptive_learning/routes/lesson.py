from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from adaptive_learning.services import lesson_service

lesson_bp = Blueprint(
    "lessons",
    __name__,
    url_prefix="/api"
)


def _json_response(service_result):
    payload, status_code = service_result
    return jsonify(payload), status_code


@lesson_bp.route("/courses/<int:course_id>/lessons", methods=["GET"])
@jwt_required()
def list_lessons(course_id):
    return _json_response(
        lesson_service.list_lessons(course_id, get_jwt().get("role"))
    )


@lesson_bp.route("/courses/<int:course_id>/lessons", methods=["POST"])
@jwt_required()
def create_lesson(course_id):
    return _json_response(
        lesson_service.create_lesson(
            course_id,
            request.get_json(silent=True),
            get_jwt().get("role")
        )
    )


@lesson_bp.route("/lessons/<int:lesson_id>", methods=["GET"])
@jwt_required()
def get_lesson(lesson_id):
    return _json_response(
        lesson_service.get_lesson(lesson_id, get_jwt().get("role"))
    )


@lesson_bp.route("/lessons/<int:lesson_id>", methods=["PUT"])
@jwt_required()
def update_lesson(lesson_id):
    return _json_response(
        lesson_service.update_lesson(
            lesson_id,
            request.get_json(silent=True),
            get_jwt().get("role")
        )
    )


@lesson_bp.route("/lessons/<int:lesson_id>", methods=["DELETE"])
@jwt_required()
def delete_lesson(lesson_id):
    return _json_response(
        lesson_service.delete_lesson(lesson_id, get_jwt().get("role"))
    )


@lesson_bp.route("/lessons/<int:lesson_id>/resources", methods=["GET"])
@jwt_required()
def list_lesson_resources(lesson_id):
    return _json_response(
        lesson_service.list_lesson_resources(
            lesson_id,
            get_jwt().get("role")
        )
    )


@lesson_bp.route("/lessons/<int:lesson_id>/resources", methods=["POST"])
@jwt_required()
def create_lesson_resource(lesson_id):
    return _json_response(
        lesson_service.create_lesson_resource(
            lesson_id,
            request.get_json(silent=True),
            get_jwt().get("role")
        )
    )


@lesson_bp.route("/lesson-resources/<int:resource_id>", methods=["GET"])
@jwt_required()
def get_lesson_resource(resource_id):
    return _json_response(
        lesson_service.get_lesson_resource(resource_id, get_jwt().get("role"))
    )


@lesson_bp.route("/lesson-resources/<int:resource_id>", methods=["PUT"])
@jwt_required()
def update_lesson_resource(resource_id):
    return _json_response(
        lesson_service.update_lesson_resource(
            resource_id,
            request.get_json(silent=True),
            get_jwt().get("role")
        )
    )


@lesson_bp.route("/lesson-resources/<int:resource_id>", methods=["DELETE"])
@jwt_required()
def delete_lesson_resource(resource_id):
    return _json_response(
        lesson_service.delete_lesson_resource(
            resource_id,
            get_jwt().get("role")
        )
    )


@lesson_bp.route("/lessons/<int:lesson_id>/learning-materials", methods=["POST"])
@jwt_required()
def upload_learning_material(lesson_id):
    return _json_response(
        lesson_service.upload_learning_material(
            lesson_id,
            request.files.get("file"),
            request.form.get("title"),
            get_jwt().get("role"),
        )
    )


@lesson_bp.route("/lesson-resources/<int:resource_id>/download", methods=["GET"])
@jwt_required()
def download_lesson_resource(resource_id):
    return lesson_service.download_lesson_resource(
        resource_id,
        get_jwt().get("role")
    )