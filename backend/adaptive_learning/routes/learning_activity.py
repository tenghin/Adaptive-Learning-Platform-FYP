from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from adaptive_learning.services import learning_activity_service

activity_bp = Blueprint(
    "learning_activity",
    __name__,
    url_prefix="/api",
)


@activity_bp.route(
    "/learning-activities",
    methods=["POST"],
)
@jwt_required()
def record_learning_activity():

    data = request.get_json(silent=True) or {}

    lesson_id = data.get("lesson_id")
    activity_type = data.get("activity_type")
    duration_seconds = data.get("duration_seconds")

    if lesson_id is None:
        return jsonify({
            "success": False,
            "message": "lesson_id is required"
        }), 400

    if activity_type is None:
        return jsonify({
            "success": False,
            "message": "activity_type is required"
        }), 400

    learning_activity_service.record_activity(
        student_id=int(get_jwt_identity()),
        lesson_id=lesson_id,
        activity_type=activity_type,
        duration_seconds=duration_seconds,
    )

    return jsonify({
        "success": True,
        "message": "Learning activity recorded."
    }), 201