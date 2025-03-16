from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_cors import CORS

# Skapa SQLAlchemy- och Migrate-instansen UTAN en app
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)  # Aktivera CORS om du behöver det

    # Initiera databasen med Flask-appen
    db.init_app(app)
    migrate.init_app(app, db)

    # Importera Blueprints EFTER att appen har skapats
    from app.routes.car import car_blueprint
    from app.routes.auth import auth_blueprint

    # from app.routes.payments import payments_blueprint

    app.register_blueprint(car_blueprint, url_prefix="/car")
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    # app.register_blueprint(payments_blueprint, url_prefix="/payments")

    return app
