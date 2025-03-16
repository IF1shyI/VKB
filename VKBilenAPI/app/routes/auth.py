from flask import Blueprint, request, jsonify
from app.services.auth_service import create_api_key

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/create_api_key", methods=["POST"])
def create_key():
    user_name = request.json.get("user_name")
    user_mail = request.json.get("user_mail")

    if not user_name or not user_mail:
        return jsonify({"error": "user_name and user_mail are required"}), 400

    api_key = create_api_key(user_name, user_mail)
    return jsonify({"api_key": api_key}), 200
