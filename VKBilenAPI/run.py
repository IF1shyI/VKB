from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)  # Lägg till detta om det saknas

if __name__ == "__main__":
    app.run(debug=True)
