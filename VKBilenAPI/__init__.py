from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()  # Lägg till Migrate här


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)  # Se till att Migrate kopplas till Flask-appen

    # Importera Blueprints efter att appen har skapats
    from app.routes.car import car_blueprint
    from app.routes.auth import auth_blueprint
    from app.routes.payments import payments_blueprint

    app.register_blueprint(car_blueprint, url_prefix="/car")
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(payments_blueprint, url_prefix="/payments")

    return app
