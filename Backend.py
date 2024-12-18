from flask import Flask, request, jsonify, session, redirect, url_for
from flask_caching import Cache
import os
import atexit
from dotenv import load_dotenv
from flask_cors import CORS
import re
import time
from openai import OpenAI
from cryptography.fernet import Fernet
from flask_session import Session
import jwt
from datetime import datetime as dt, timedelta  # Importera datetime som dt
import hashlib
import json


# http://127.0.0.1:5000/

app = Flask(__name__)
CORS(app, supports_credentials=True)


app.secret_key = os.urandom(24)

app.config["SESSION_COOKIE_SECURE"] = False  # Aktivera endast om du kör HTTPS
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Tillåt cross-site requests med cookies

# Ladda miljövariabler från .env-filen
load_dotenv()

# Hämta användarnamn och lösenord från miljövariabler
USERNAME = os.getenv("USERN")
PASSWORD = os.getenv("PASSWORD")
APIKEY = os.getenv("APIKEY")
encryption_key = os.getenv("ENCRTPT_KEY")
Session_key = os.getenv("SESS_KEY")

client = OpenAI(
    # This is the default and can be omitted
    api_key=APIKEY,
)

global_car_model = "No model found"

# Konfigurera cachen
cache = Cache(
    app,
    config={
        "CACHE_TYPE": "SimpleCache",  # Typ av cache, enkel i minnet cache
        "CACHE_DEFAULT_TIMEOUT": 300,  # Timeout för cachade resultat (i sekunder)
    },
)

SESSION_FILE = "session.json"  # Fil för att lagra sessionen
SESSION_FILE_AI = "sessionai.json"  # Fil för att lagra sessionen
global_besbruk = "Error"
global_fskatt = "Error"
drivmedel = "Error"
co2 = "Error"

app.secret_key = Session_key

# Använd serverbaserade sessioner (sessioner som sparas på servern)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SECURE"] = False

Session(app)


@app.route("/submit-form", methods=["POST"])
def submit_form():
    try:
        # Hämta data från förfrågan
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        subject = data.get("subject")
        message = data.get("message")

        # Debug-loggning
        print(f"Name: {name}, Email: {email}, Subject: {subject}")

        # Skapa innehållet i Markdown-format
        markdown_content = f"""
# Kontaktforfragan

**Namn**: {name}  
**Email**: {email}  
**Ämne**: {subject}  

**Meddelande**:  
{message}

---

Datum: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        # Definiera filnamn och filväg
        file_name = f"contact_{int(dt.now().timestamp())}.md"
        feedback_directory = os.path.join(os.getcwd(), "feedback")

        # Skapa mappen "feedback" om den inte finns
        os.makedirs(feedback_directory, exist_ok=True)

        file_path = os.path.join(feedback_directory, file_name)

        # Skriv markdown-innehållet till filen
        with open(file_path, "w") as f:
            f.write(markdown_content)

        # Bekräfta skapad fil
        print(f"Markdown-fil skapad: {file_path}")
        return jsonify({"message": "Formulärdata mottaget och sparat."}), 200

    except Exception as e:
        print(f"Fel vid skapandet av Markdown-filen: {e}")
        return jsonify({"error": "Serverfel. Kunde inte spara meddelandet."}), 500


@app.route("/tips", methods=["GET"])
def tips():

    tips_trix_promt = f"Ge en lista med de fem viktigaste tipsen för att minska utsläppen och göra en {global_car_model} mer miljövänlig och kostnadseffektiv. Fokusera på att förbättra bränsleeffektivitet, minska koldioxidutsläpp och optimera långsiktiga kostnadsbesparingar. Inkludera både tips för körvanor och bilunderhåll. Avsluta med en uppskattning av hur mycket utsläpp och pengar man kan spara med dessa åtgärder."
    print("Prompten är:", tips_trix_promt)

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": tips_trix_promt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    maintenancecost = response.choices[0].message.content

    print("Svaret från ai: ", maintenancecost)


# Markdown-fil där användardata sparas
DATA_FILE = "users.md"
ADMIN_FILE = "admin.md"

KEY = encryption_key  # Ersätt med en riktig nyckel
SECRET_KEY = encryption_key
ALGORITHM = "HS256"
TOKEN_EXPIRATION_MINUTES = 120
cipher_suite = Fernet(KEY)


def encrypt_data(data: str) -> str:
    return cipher_suite.encrypt(data.encode()).decode()


def decrypt_data(data: str) -> str:
    return cipher_suite.decrypt(data.encode()).decode()


def write_to_md_file(encrypted_data: str, FILE):
    with open(FILE, "a") as file:
        file.write(encrypted_data + "\n")


def read_from_md_file(FILE):
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r") as file:
        lines = file.readlines()
    return [decrypt_data(line.strip()) for line in lines]


# Hjälpfunktion för att generera JWT
def generate_jwt(username: str) -> str:
    expiration = dt.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
    payload = {
        "username": username,
        "exp": expiration,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


# Hjälpfunktion för att verifiera JWT
def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Returnerar användardata från tokenen
    except jwt.ExpiredSignatureError:
        return None  # Token har gått ut
    except jwt.InvalidTokenError:
        return None  # Token är ogiltig


# Registreringsrutt
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    password = data.get("password")
    Tier = "PP"

    users = read_from_md_file(DATA_FILE)
    for user_data in users:
        # Split the decrypted data into fields
        user_fields = user_data.split(", ")
        existing_name = user_fields[0].split(": ")[1]  # Extract 'Name' field
        if existing_name == name:
            return (
                jsonify({"message": "Användarnamn är redan taget", "success": False}),
                409,
            )
    # Kryptera data
    user_data = f"Name: {name}, Password: {password}, Tier: {Tier}"
    encrypted_data = encrypt_data(user_data)

    # Skriv krypterad data till .md-filen
    write_to_md_file(encrypted_data, DATA_FILE)

    return jsonify({"message": "Användare registrerad och data sparad"}), 200


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Läs användardata från filen
    users = read_from_md_file(DATA_FILE)

    # Kontrollera om användaren finns och om lösenordet stämmer
    for user in users:
        # Dela upp den dekrypterade data för att få ut namn och lösenord
        user_data = user.split(", ")
        user_name = user_data[0].split(": ")[1]
        user_password = user_data[1].split(": ")[1]

        # Jämför namn och lösenord
        if user_name == username and user_password == password:
            token = generate_jwt(username)  # Skapa JWT för användaren
            return (
                jsonify(
                    {"message": "Inloggning lyckades!", "token": token, "success": True}
                ),
                200,
            )

    return (
        jsonify({"message": "Fel användarnamn eller lösenord", "success": False}),
        401,
    )


@app.route("/logout", methods=["POST"])
def logout():
    try:
        # Hämta Authorization-headern från begäran
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Token saknas eller är ogiltig"}), 401

        # Extrahera JWT-token
        token = auth_header.split(" ")[1]

        # Verifiera JWT-token
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token har gått ut"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Ogiltig token"}), 401

        # Om verifieringen lyckas, logga ut användaren (rensa sessionen)
        session.pop("user", None)

        # Returnera en framgångsrik respons
        return jsonify({"message": "Utloggning lyckades"}), 200

    except Exception as e:
        return jsonify({"message": f"Något gick fel: {str(e)}"}), 500


@app.route("/checksession", methods=["GET"])
def check_session():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"message": "Ingen token tillhandahållen"}), 401

    token = auth_header.split(" ")[1]
    try:
        # Dekryptera JWT för att få användardata
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = decoded_token.get("username")
        if username:
            return jsonify({"message": "Session giltig", "username": username}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token har gått ut"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Ogiltig token"}), 401

    return jsonify({"message": "Ogiltig session"}), 401


@app.route("/checktier", methods=["GET"])
def check_tier():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"message": "Ingen token tillhandahållen"}), 401

    token = auth_header.split(" ")[1]

    try:
        # Dekryptera JWT för att få användardata
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username_from_token = decoded_token.get("username")

        if not username_from_token:
            return jsonify({"message": "Ingen användare i token"}), 401

        # Läs användardata från markdown-fil
        users = read_from_md_file(DATA_FILE)

        # Kontrollera om användaren finns och om lösenordet stämmer
        for user in users:
            # Dela upp den dekrypterade data för att få ut namn och lösenord
            user_data = user.split(", ")
            user_name = user_data[0].split(": ")[1]
            user_tier = user_data[2].split(": ")[1]

            if user_tier == "FA":
                return_tier = "ftag"
            elif user_tier == "PA":
                return_tier = "pro"
            elif user_tier == "BA":
                return_tier = "bas"
            else:
                return_tier = "privat"

            if user_name == username_from_token:
                return (
                    jsonify({"message": "Användare hittad", "tier": return_tier}),
                    200,
                )

        return jsonify({"message": "Användare ej hittad"}), 404

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token har gått ut"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Ogiltig token"}), 401


@app.route("/admin", methods=["POST"])
def check_admin():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"message": "Ingen token tillhandahållen"}), 401

    token = auth_header.split(" ")[1]

    try:
        # Dekryptera JWT för att få användardata
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username_from_token = decoded_token.get("username")

        if not username_from_token:
            return jsonify({"message": "Ingen användare i token"}), 401

        # Läs användardata från markdown-fil
        users = read_from_md_file(DATA_FILE)

        admin_users = read_from_md_file(ADMIN_FILE)
        print(admin_users)

        # Kontrollera om användaren finns och om lösenordet stämmer
        for user in users:
            # Dela upp den dekrypterade data för att få ut namn och lösenord
            user_data = user.split(", ")
            user_name = user_data[0].split(": ")[1]
            if user_name == username_from_token:
                for admins in admin_users:
                    user_fields = admins.split(", ")
                    admin_name = user_fields[0].split(": ")[1]  # Extract 'Name' field
                    if user_name == admin_name:
                        return jsonify({"message": "Autentiserad"}), 200
        return jsonify({"message": "Oautentiserad"}), 401

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token har gått ut"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Ogiltig token"}), 401


def create_admin(username):
    admin_users = read_from_md_file(ADMIN_FILE)
    for user_data in admin_users:
        # Split the decrypted data into fields
        user_fields = user_data.split(", ")
        existing_name = user_fields[0].split(": ")[1]  # Extract 'Name' field
        if existing_name == username:
            return (
                jsonify({"message": "Användarnamn är redan taget", "success": False}),
                409,
            )
    user_data = f"Name: {username}"
    encrypted_data = encrypt_data(user_data)

    # Skriv krypterad data till .md-filen
    write_to_md_file(encrypted_data, ADMIN_FILE)


# Sökdata fil
SEARCH_DATA_FILE = "search_data.json"

# Max antal sökningar per timme för olika grupper
MAX_SEARCHES = {
    "bas": 10,  # Administratörer får göra 100 sökningar per timme
    "privat": 5,  # Vanliga användare får göra 10 sökningar per timme
}
UNLIMITED_SEARCH_GROUPS = ["ftag", "pro"]


# Läs sökdata från fil
def load_search_data():
    if os.path.exists(SEARCH_DATA_FILE):
        with open(SEARCH_DATA_FILE, "r") as file:
            return json.load(file)
    return {}


# Spara sökdata till fil
def save_search_data(data):
    with open(SEARCH_DATA_FILE, "w") as file:
        json.dump(data, file)


# Kolla om användaren har överskridit max antal sökningar
def check_search_limit(user_name, user_tier):
    data = load_search_data()

    # Om användaren inte finns, skapa en ny post
    if user_name not in data:
        data[user_name] = {
            "search_count": 0,
            "last_reset": dt.now().isoformat(),
        }
        save_search_data(data)

    user_data = data[user_name]
    last_reset = dt.fromisoformat(user_data["last_reset"])
    current_time = dt.now()

    # Om en timme har gått, återställ räknaren
    if current_time - last_reset >= timedelta(hours=1):
        user_data["search_count"] = 0
        user_data["last_reset"] = current_time.isoformat()
        save_search_data(data)

    # Om användaren tillhör en obegränsad grupp, ge obegränsade sökningar
    if user_tier in UNLIMITED_SEARCH_GROUPS:
        return True, "Du har obegränsade sökningar."

    # Kolla om användaren har överskridit gränsen
    max_searches = MAX_SEARCHES.get(user_tier, 5)

    if user_data["search_count"] >= max_searches:
        return False, f"Max antal sökningar per timme är {max_searches} för din grupp."

    # Annars, öka sökräknaren och spara
    user_data["search_count"] += 1
    save_search_data(data)
    return (
        True,
        f"Du har {max_searches - user_data['search_count']} sökningar kvar denna timme.",
    )


@app.route("/can_search", methods=["GET"])
def can_search():
    auth_header = request.headers.get("Authorization")
    user_tier = request.args.get("user_tier")
    if not auth_header:
        return jsonify({"message": "Ingen token tillhandahållen"}), 401

    token = auth_header.split(" ")[1]

    try:
        # Dekryptera JWT för att få användardata
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username_from_token = decoded_token.get("username")

        # Kontrollera om användaren har överskridit max antal sökningar
        is_allowed, message = check_search_limit(username_from_token, user_tier)

        # Returnera en JSON med true/false beroende på om användaren kan söka
        return jsonify({"can_search": is_allowed, "message": message})
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token har gått ut"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Ogiltig token"}), 401


if __name__ == "__main__":
    app.run(debug=False, port=5000)


# if "user" not in session:
#     return redirect(url_for("login"))

# PP = privatperson PA = Professionell användare FA = Företagsanvändare
