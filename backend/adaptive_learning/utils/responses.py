from flask import jsonify


def success_response(message, data=None, status_code=200):
    payload = {
        "success": True,
        "message": message,
        "data": data or {}
    }
    return jsonify(payload), status_code


def error_response(message, status_code=400):
    payload = {
        "success": False,
        "message": message
    }
    return jsonify(payload), status_code
