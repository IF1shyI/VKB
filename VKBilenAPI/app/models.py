from app import db
from datetime import datetime
import uuid


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
    reg_plate = db.Column(db.String(20), unique=True, nullable=False)
    model = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    cost_per_month = db.Column(db.Float)
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
