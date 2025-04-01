from flask import Blueprint, request, jsonify
from app.services.car_finder import get_car_info
from app.services.auth_service import verify_api_key
from app.utils.helpers import search_by_regnumber, today_fuelprice

car_blueprint = Blueprint("car", __name__)


@car_blueprint.route("/cost", methods=["GET"])
async def car_cost_month():
    # Hämta reg_plate från query-parametrarna
    reg_plate = request.args.get("reg_plate")

    data = search_by_regnumber(reg_plate, "vehicles.json")

    if data:

        car_data = {
            "regnr": reg_plate,
            "success": True,
            "status": "Data hämtad",
            "car_info": data,
        }

    if data:
        await today_fuelprice(car_data["car_info"])

    else:
        car_data = await get_car_info(reg_plate)

    # Kolla om biluppgifterna finns
    if car_data:
        return jsonify({"message": "Car data found", "data": car_data}), 200
    else:
        return jsonify({"message": "Car not found"}), 404


@car_blueprint.route("/test", methods=["GET"])
async def test():
    # Hämta reg_plate från query-parametrarna
    reg_plate = request.args.get("reg_plate")

    data = search_by_regnumber(reg_plate, "vehicles.json")

    if data:

        car_data = {
            "regnr": reg_plate,
            "success": True,
            "status": "Data hämtad",
            "car_info": data,
        }

    if data:
        await today_fuelprice(car_data["car_info"])

    else:
        car_data = await get_car_info(reg_plate)

    # Kolla om biluppgifterna finns
    if car_data:
        return jsonify({"message": "Car data found", "data": car_data}), 200
    else:
        return jsonify({"message": "Car not found"}), 404
