from app.models import db, Car


def get_car_info(reg_plate):
    car = Car.query.filter_by(reg_plate=reg_plate).first()
    if car:
        return {
            "reg_plate": car.reg_plate,
            "brand": car.brand,
            "model": car.model,
            "cost_per_month": car.cost_per_month,
        }
    return {"error": "Car not found"}
