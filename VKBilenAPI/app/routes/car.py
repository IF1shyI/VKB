from flask import Blueprint, request, jsonify
from app.services.car_service import get_car_info

car_blueprint = Blueprint("car", __name__)


@car_blueprint.route("/cost", methods=["GET"])
def car_cost_month():
    reg_plate = request.args.get("reg_plate")
    api_key = request.args.get("key")

    car_data = get_car_info(reg_plate, api_key)
    if "error" in car_data:
        return jsonify(car_data), 400
    return jsonify(car_data), 200
