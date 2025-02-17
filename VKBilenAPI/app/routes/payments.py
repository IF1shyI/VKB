from flask import Blueprint, jsonify

payments_blueprint = Blueprint("payments", __name__)


@payments_blueprint.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "Payments route works!"})
