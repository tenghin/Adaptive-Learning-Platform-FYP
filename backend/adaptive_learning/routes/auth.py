from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from adaptive_learning.services import auth_service

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


def _json_response(service_result):
    payload, status_code = service_result
    return jsonify(payload), status_code


@auth_bp.route("/register", methods=["POST"])
def register_user():
    return _json_response(
        auth_service.register(request.get_json(silent=True))
    )


@auth_bp.route("/login", methods=["POST"])
def login_user():
    return _json_response(
        auth_service.login(request.get_json(silent=True))
    )


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    return _json_response(
        auth_service.get_profile(get_jwt_identity())
    )


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    return _json_response(
        auth_service.change_password(
            get_jwt_identity(),
            request.get_json(silent=True)
        )
    )


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    return _json_response(
        auth_service.forgot_password(request.get_json(silent=True))
    )


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    return _json_response(
        auth_service.reset_password(request.get_json(silent=True))
    )
