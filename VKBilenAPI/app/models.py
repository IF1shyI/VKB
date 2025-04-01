from app import db
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import ARRAY


# API-nycklar
class API(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_mail = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_name, user_mail):
        self.user_name = user_name
        self.user_mail = user_mail
        self.api_key = str(uuid.uuid4())


# Bilinformation
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_plate = db.Column(db.String(20), unique=True, nullable=False)  # "reg"
    model = db.Column(db.String(100), nullable=False)  # "model"
    brand = db.Column(db.String(100), nullable=False)  # "make"
    year = db.Column(db.Integer)  # "year"
    car_type = db.Column(db.String(50))  # "type"
    fuel_type = db.Column(ARRAY(db.String))  # "fuel_type" (Array av strängar)
    drive_wheels = db.Column(db.String(10))  # "drive_wheels"
    horsepower = db.Column(db.Float)  # "horsepower"
    fuel_consumption = db.Column(db.Float)  # "fuel_consumption"
    co2_emission = db.Column(db.Float)  # "co2_emission"
    monthly_tax = db.Column(db.Float)  # "monthly_tax"
    insurance = db.Column(db.Float)  # "insurance"
    maintenance_tires = db.Column(db.Float)  # "maintenance" - tires
    maintenance_service = db.Column(db.Float)  # "maintenance" - service
    cost_per_month = db.Column(
        db.Float
    )  # Totala månadskostnaden (om du vill inkludera)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Betalningar
# class Payment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(
#         db.Integer, db.ForeignKey("API.id"), nullable=False
#     )  # Korrekt ForeignKey-referens
#     amount = db.Column(db.Float, nullable=False)
#     date = db.Column(db.DateTime, default=datetime.utcnow)

#     user = db.relationship("API", backref="payments")
