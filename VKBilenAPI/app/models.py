from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()


# API-nycklar
class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_name):
        self.user_name = user_name
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
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("api_key.id"))
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("APIKey", backref="payments")
