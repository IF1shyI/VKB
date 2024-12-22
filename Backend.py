from flask import Flask, request, jsonify, session, redirect, url_for
from flask_caching import Cache
import os
import atexit
from dotenv import load_dotenv
from flask_cors import CORS
import re
import time
from openai import OpenAI
from cryptography.fernet import Fernet, InvalidToken
from flask_session import Session
import jwt
from datetime import datetime as dt, timedelta  # Importera datetime som dt
import hashlib
import json
import stripe
import jwt
import uuid
import base64


def fix_base64_padding(data: str) -> str:
    # Lägg till padding om den saknas
    padding = len(data) % 4
    if padding != 0:
        data += "=" * (4 - padding)
    return data


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
stripe_key = os.getenv("STRIPE_KEY")
fernet_key = os.getenv("FERNET_KEY")

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

SECRET_KEY = encryption_key
ALGORITHM = "HS256"
TOKEN_EXPIRATION_MINUTES = 120
cipher_suite = Fernet(fernet_key)


def encrypt_data(data: str) -> str:
    return cipher_suite.encrypt(data.encode()).decode()


def decrypt_data(data: str) -> str:
    try:
        # Försök att fixa base64-padding innan dekryptering
        fixed_data = fix_base64_padding(data)
        return cipher_suite.decrypt(fixed_data.encode()).decode()
    except InvalidToken:
        raise ValueError("Ogiltig token eller fel vid dekryptering.")


def write_to_md_file(data, DATA_FILE):
    """
    Skriver krypterad data till fil. Data bör vara en lista av krypterade strängar.
    """
    if not isinstance(data, (list, tuple)):
        raise ValueError(
            "Data måste vara en lista eller itererbar av krypterade strängar."
        )

    with open(DATA_FILE, "w") as file:
        for encrypted_data in data:
            file.write(str(encrypted_data) + "\n")


def read_from_md_file(FILE):
    """
    Läser krypterad data från fil och försöker dekryptera varje rad.
    Ignorerar rader som inte kan dekrypteras.
    """
    if not os.path.exists(FILE):
        return []

    decrypted_data = []
    with open(FILE, "r") as file:
        lines = file.readlines()

    for line in lines:
        try:
            decrypted_line = decrypt_data(line.strip())
            decrypted_data.append(decrypted_line)
        except ValueError as e:
            print(f"Fel vid dekryptering av rad: {line.strip()} - {str(e)}")
            # Ignorera trasiga rader och fortsätt
            continue

    return decrypted_data


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
    """
    Verifierar en JWT-token och returnerar dess payload om den är giltig.

    :param token: JWT-token som ska verifieras
    :return: Dictionary med payload-data om token är giltig, annars None
    """
    try:
        # Försök att dekoda token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Returnerar användardata från tokenen
    except jwt.ExpiredSignatureError:
        print("Fel: Token har gått ut.")  # Logga eller hantera utgången token
        return None
    except jwt.InvalidTokenError as e:
        print(
            f"Fel: Ogiltig token. Detaljer: {str(e)}"
        )  # Logga eller hantera ogiltig token
        return None
    except Exception as e:
        print(f"Ett oväntat fel inträffade: {str(e)}")  # För generella fel
        return None


# Registreringsrutt
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    password = data.get("password")
    mail = data.get("email")
    tier = "PP"

    # Läs existerande användare
    users = read_from_md_file(DATA_FILE)

    # Kontrollera om användarnamnet redan finns
    for user_data in users:
        user_fields = user_data.split(", ")
        existing_name = user_fields[1].split(": ")[1]  # Extract 'username' field
        if existing_name == name:
            return (
                jsonify({"message": "Användarnamn är redan taget", "success": False}),
                409,
            )

    # Generera ett unikt user_id
    user_id = str(uuid.uuid4())

    # Skapa användardata i klartext
    user_data = f"UserID: {user_id}, username: {name}, password: {password}, Tier: {tier}, mail: {mail}"

    # Kryptera användardata
    encrypted_data = encrypt_data(user_data)

    # Lägg till den nya krypterade användardatan i listan
    users.append(encrypted_data)

    # Skriv tillbaka hela listan till filen
    write_to_md_file(users, DATA_FILE)

    return (
        jsonify(
            {"message": "Användare registrerad och data sparad", "user_id": user_id}
        ),
        200,
    )


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
        user_name = user_data[1].split(": ")[1]
        user_password = user_data[2].split(": ")[1]

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
            user_name = user_data[1].split(": ")[1]
            user_tier = user_data[3].split(": ")[1]

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


@app.route("/can_search_ip", methods=["GET"])
def can_search_ip():
    user_ip = request.args.get("user_ip")
    if not user_ip:
        return jsonify({"message": "Ingen ip tillhandahållen"}), 401

    try:

        # Kontrollera om användaren har överskridit max antal sökningar
        is_allowed, message = check_search_limit(user_ip, "none")

        # Returnera en JSON med true/false beroende på om användaren kan söka
        return jsonify({"can_search": is_allowed, "message": message})
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token har gått ut"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Ogiltig token"}), 401


def get_user_by_jwt(token):
    """
    Hämtar användardata baserat på en JWT-token.
    :param token: JWT-token
    :return: Dictionary med användar-ID och namn, eller None om misslyckas
    """
    try:
        # Steg 1: Kontrollera JWT-token
        payload = verify_jwt(token)
        if not payload:
            print("JWT-token är ogiltig eller har gått ut.")
            return None

        print("Decoded payload:", payload)

        # Steg 2: Hämta användarnamn från payload
        username = payload.get("username")
        if not username:
            print("Username saknas i JWT-payload.")
            return None

        # Steg 3: Läs och validera användardata från filen
        users = read_from_md_file(DATA_FILE)
        if not users:
            print("Inga användare hittades i filen.")
            return None

        for user in users:
            try:
                user_fields = user.split(", ")

                user_id = user_fields[0].split(": ")[1]
                user_name = user_fields[1].split(": ")[1]
                user_email = user_fields[4].split(": ")[1]

                if user_name == username:
                    print(f"Användare hittad: {username}")
                    return {"id": user_id, "name": user_name, "email": user_email}
            except Exception as e:
                print(f"Fel vid bearbetning av användardata: {str(e)}")
                continue

        print("Ingen användare matchade det angivna användarnamnet.")
        return None

    except Exception as e:
        print(f"Fel vid dekodning av JWT: {str(e)}")
        return None


@app.route("/update_tier", methods=["POST"])
def update_tier():
    # Hämta JWT från headers (om du använder JWT för autentisering)
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"message": "Ingen autentisering tillhandahölls."}), 403

    token = auth_header.split(" ")[1]  # Anta att JWT är i formatet 'Bearer <token>'

    # Verifiera JWT-token och hämta användaren
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username_from_token = decoded_token.get("username")
        if not username_from_token:
            return jsonify({"message": "Ingen användare i token"}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token har gått ut"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Ogiltig token"}), 401

    # Hämta new_tier från request body
    data = request.get_json()
    new_tier = data.get("new_tier")
    print("Tier: ", new_tier)

    if new_tier == "basanvandare":
        new_tier = "BA"
    elif new_tier == "professionell":
        new_tier = "PA"

    if not new_tier:
        return jsonify({"message": "Ingen ny tier angavs."}), 400

    # Läs användardata från markdown-fil
    users = read_from_md_file(DATA_FILE)

    # Kontrollera om användaren finns och uppdatera deras tier
    user_found = False
    updated_data = []

    print(users)

    for user in users:
        print(user)
        # Dela upp den dekrypterade data för att få ut användarnamn och tier
        user_fields = user.split(", ")
        user_name = user_fields[1].split(": ")[1]  # Extract 'Name' field
        user_tier = user_fields[3].split(": ")[1]  # Extract 'Tier' field
        user_id = user_fields[0].split(": ")[1]  # Extract 'UserID' field

        # Om användaren matchar den från token, uppdatera tier
        if user_name == username_from_token:
            user_found = True
            updated_user_data = f"UserID: {user_id}, username: {user_name}, password: {user_fields[2].split(': ')[1]}, Tier: {new_tier}, mail: {user_fields[4].split(': ')[1]}"
            encrypted_data = encrypt_data(updated_user_data)
            updated_data.append(encrypted_data)
        else:
            updated_data.append(user)

    if not user_found:
        return jsonify({"message": "Användare ej hittad"}), 404

    # Skriv tillbaka den uppdaterade användardatan i filen
    write_to_md_file(updated_data, DATA_FILE)

    return jsonify({"message": f"Tier uppdaterad till {new_tier}."}), 200


stripe.api_key = stripe_key


@app.route("/secret_key", methods=["POST"])
def secret_key():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"message": "Ingen autentisering tillhandahölls."}), 403

    data = request.get_json()
    tierPrice = data.get("tierPrice")
    customerName = data.get("customerName")  # Få kundens namn från begäran
    customerEmail = data.get("customerEmail")  # Få kundens e-post från begäran

    if not tierPrice:
        return jsonify({"message": "TierPrice saknas i begäran."}), 400

    try:
        # Skapa en kund i Stripe
        customer = stripe.Customer.create(
            name=customerName,
            email=customerEmail,
        )
        print(customer)

        # Skapa en PaymentIntent kopplad till kunden
        payment_intent = stripe.PaymentIntent.create(
            amount=int(tierPrice) * 100,  # Belopp i öre (100 = 1 SEK)
            currency="sek",
            customer=customer.id,  # Koppla PaymentIntent till kunden
        )

        # Skicka tillbaka client_secret
        return jsonify(
            {
                "client_secret": payment_intent.client_secret,
                "customer_id": customer.id,  # Skicka tillbaka kundens ID (valfritt)
            }
        )

    except Exception as e:
        return jsonify(error=str(e)), 400


if __name__ == "__main__":
    app.run(debug=False, port=5000)


# if "user" not in session:
#     return redirect(url_for("login"))

# PP = privatperson PA = Professionell användare FA = Företagsanvändare
