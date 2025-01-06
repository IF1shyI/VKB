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
from datetime import datetime as dt, timedelta, timezone  # Importera datetime som dt
import hashlib
import json
import stripe
import jwt
import uuid
import base64
import ast


def fix_base64_padding(data: str) -> str:
    # Lägg till nödvändiga padding-tecken till base64-strängen
    return data + "=" * (4 - len(data) % 4) if len(data) % 4 else data


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


def encrypt_data(data):
    # Om data är en lista, konvertera den till en JSON-sträng
    if isinstance(data, list):
        data = json.dumps(data)  # Konvertera listan till en JSON-sträng

    # Kryptera strängen
    encrypted_data = cipher_suite.encrypt(
        data.encode()
    ).decode()  # Kryptera och konvertera till sträng

    return encrypted_data


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
        # Om data inte är en lista, gör den till en lista med ett enda element
        data = [data]

    # Kontrollera att varje element i data är en krypterad sträng
    for item in data:
        if not isinstance(item, str):  # Kontrollera att det är en sträng
            raise ValueError("Varje element i data måste vara en krypterad sträng.")

    # Skriv data till fil
    with open(DATA_FILE, "w") as file:
        for encrypted_data in data:
            # Skriv den krypterade strängen direkt utan att använda str()
            file.write(
                encrypted_data + "\n"
            )  # "\n" läggs till här för att separera varje rad


def read_from_md_file(FILE):
    """
    Läser krypterad data från fil och försöker dekryptera varje rad.
    Ignorerar rader som inte kan dekrypteras.
    """
    if not os.path.exists(FILE):
        return

    decrypted_data = []
    with open(FILE, "r") as file:
        lines = file.readlines()

    for line in lines:
        print(line)
        try:
            decrypted_line = decrypt_data(line.strip())
            decrypted_data.append(decrypted_line)
        except ValueError as e:
            print(f"Fel vid dekryptering av rad: {line.strip()} - {str(e)}")
            # Ignorera trasiga rader och fortsätt
            continue
    real_data = make_list_from_string(decrypted_data)

    return real_data


def make_list_from_string(data):
    print("datastring: ", data)

    # Kontrollera om data är en lista, och om så, gör om till en sträng
    if isinstance(data, list):
        data_str = "".join(data)  # Om det är en lista, sammanfoga till en sträng
    else:
        data_str = data  # Om data redan är en sträng

    # Dela upp strängen där vi hittar '',' och ta bort överskottstecken
    split_data = data_str.split("','")

    # Rensa bort ' från första och sista elementet om det finns
    split_data = [item.strip("'") for item in split_data]

    print("splitdata: ", split_data)
    return split_data


# Hjälpfunktion för att generera JWT
def generate_jwt(username: str) -> str:
    expiration = dt.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)

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


###########################################################################################################################
#                                                   Profile
###########################################################################################################################


@app.route("/profileinfo", methods=["POST"])
def profileinfo():
    try:
        # Hämta Authorization-headern från begäran
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Token saknas eller är ogiltig"}), 401

        # Extrahera JWT-token
        token = auth_header.split(" ")[1]

        # Verifiera JWT-token
        data = get_user_by_jwt(token)
        data.pop("id", None)
        return data
    except Exception as e:
        return jsonify({"message": f"Något gick fel: {str(e)}"}), 500


@app.route("/updateprofile", methods=["POST"])
def updateprofile():
    # Hämta data från begäran
    firstname = request.json.get("firstname")
    lastname = request.json.get("lastname")
    username = request.json.get("username")
    email = request.json.get("email")

    try:
        # Hämta Authorization-headern från begäran
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Token saknas eller är ogiltig"}), 401

        # Extrahera JWT-token
        token = auth_header.split(" ")[1]

        # Verifiera JWT-token och hämta användardata
        current_data = get_user_by_jwt(token)

        if not current_data:
            return jsonify({"message": "Ogiltig eller utgången token"}), 401

        # Uppdatera användardatan med nya värden om de finns
        updated_data = current_data.copy()

        print("Namn: ", firstname)

        if firstname is not None:
            updated_data["firstname"] = firstname

        if lastname is not None:
            updated_data["lastname"] = lastname

        if username is not None:
            updated_data["username"] = username

        if email is not None:
            updated_data["email"] = email

        print("uppdated data: ", updated_data)
        # Spara uppdaterad data till databas eller fil
        save_user_data(updated_data)

        return (
            jsonify({"message": "Profil uppdaterad", "updated_data": updated_data}),
            200,
        )
    except Exception as e:
        return jsonify({"message": f"Något gick fel: {str(e)}"}), 500


def save_user_data(data):
    try:
        # Läs och validera användardata från filen
        users = read_from_md_file(DATA_FILE)
        if not users:
            print("Inga användare hittades i filen.")
            return None

        updated_users = []  # Lista för att hålla uppdaterad användardata

        for user in users:
            try:
                user_fields = user.split(", ")

                user_id = user_fields[0].split(": ")[1]
                user_name = user_fields[1].split(": ")[1]
                user_psw = user_fields[2].split(": ")[1]
                user_tier = user_fields[3].split(": ")[1]
                user_mail = user_fields[4].split(": ")[1]
                user_firstname = user_fields[5].split(": ")[1]
                user_lastname = user_fields[6].split(": ")[1]

                # Kontrollera om användar-ID matchar
                if user_id == data.get("id"):
                    print("Match hittad", data)

                    # Hämta värden med standardvärden om nycklar saknas
                    username = data.get("username", user_name)
                    password = data.get("password", user_psw)
                    tier = data.get("tier", user_tier)
                    email = data.get("email", user_mail)
                    firstname = data.get("firstname", user_firstname)
                    lastname = data.get("lastname", user_lastname)

                    # Formatera den uppdaterade användardatan
                    user_data = (
                        f"UserID: {user_id}, "
                        f"username: {username}, "
                        f"password: {password}, "
                        f"Tier: {tier}, "
                        f"mail: {email}, "
                        f"firstname: {firstname}, "
                        f"lastname: {lastname}"
                    )

                    print("Userdata: ", user_data)

                    # Lägg till uppdaterad data till listan
                    updated_users.append(user_data)
                else:
                    # Lägg till befintlig data för användare som inte matchar
                    updated_users.append(user)
            except Exception as e:
                print(f"Fel vid bearbetning av användardata: {str(e)}")
                continue

        # Skriv tillbaka hela listan till filen
        newstring = ""

        for i, content in enumerate(updated_users):
            # Kolla om innehållet redan har ' i början och slutet
            if not content.startswith("'") or not content.endswith("'"):
                data = f"'{content}'"
            else:
                data = content

            # Om det inte är sista raden, lägg till ett komma
            if i < len(users) - 1:
                data += ","

            newstring += data

        encrypted_data = encrypt_data(newstring)
        write_to_md_file(encrypted_data, DATA_FILE)
        print("Användardata har sparats.")
    except Exception as e:
        print(f"Fel vid bearbetning av användardata: {str(e)}")
        return None


###########################################################################################################################
#                                                   LOGIN/LOGOUT
###########################################################################################################################


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

    print("Users before: ", users)

    new_userdata = []
    # Kontrollera om användarnamnet redan finns
    for user_data in users:
        user_fields = user_data.split(", ")
        existing_name = user_fields[1].split(": ")[1]  # Extract 'username' field
        if existing_name == name:
            return (
                jsonify({"message": "Användarnamn är redan taget", "success": False}),
                409,
            )
        else:
            new_userdata.append(user_data)

    # Generera ett unikt user_id
    user_id = str(uuid.uuid4())

    # Skapa användardata i klartext
    user_data = (
        f"UserID: {user_id}, username: {name}, password: {password}, Tier: {tier}, mail: {mail}, firstname: "
        ", lastname: "
        ""
    )

    users.append(user_data)

    newstring = ""

    for i, content in enumerate(users):
        # Kolla om innehållet redan har ' i början och slutet
        if not content.startswith("'") or not content.endswith("'"):
            data = f"'{content}'"
        else:
            data = content

        # Om det inte är sista raden, lägg till ett komma
        if i < len(users) - 1:
            data += ","

        newstring += data

    print("newstring: ", newstring)
    encrypted_data = encrypt_data(newstring)

    # Skriv tillbaka hela listan till filen
    write_to_md_file(encrypted_data, DATA_FILE)

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

    print(users)

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
            print("User tier: ", user_tier)

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
        token_data = get_user_by_jwt(token)

        if not token_data:
            return jsonify({"message": "Ingen användare i token"}), 401

        # Läs användardata från markdown-fil
        users = read_from_md_file(DATA_FILE)

        admin_users = read_from_md_file(ADMIN_FILE)

        # Kontrollera om användaren finns och om lösenordet stämmer
        for user in users:
            # Dela upp den dekrypterade data för att få ut namn och lösenord
            user_data = user.split(", ")
            user_id = user_data[0].split(": ")[1]
            if user_id == token_data["id"]:
                for admins in admin_users:
                    # Förvandla strängen till en dictionary
                    admin_data = ast.literal_eval(
                        admins
                    )  # Omvandla strängen till en dictionary
                    admin_name = admin_data.get("Name")  # Extrahera värdet av 'Name'

                    if (
                        token_data["id"] == admin_name
                    ):  # Här kontrollerar du om ID:t matchar
                        return jsonify({"message": "Autentiserad"}), 200
        return jsonify({"message": "Oautentiserad"}), 401

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token har gått ut"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Ogiltig token"}), 401
    except Exception as e:
        return jsonify({"message": f"Fel: {str(e)}"}), 500


def create_admin(username):
    admin_users = read_from_md_file(ADMIN_FILE)
    users = read_from_md_file(DATA_FILE)

    for user_data in admin_users:
        # Split the decrypted data into fields
        admin_data = ast.literal_eval(
            admin_data
        )  # Omvandla strängen till en dictionary
        admin_id = admin_data.get("Name")  # Extract 'Name' field
        if admin_id == username:
            return (
                jsonify({"message": "Användarnamn är redan taget", "success": False}),
                409,
            )

    for user in users:
        user_fields = user.split(", ")
        user_name = user_fields[1].split(": ")[1]
        user_id = user_fields[0].split(": ")[1]

        if username == user_name:
            # Skapa en dictionary med 'Name' som nyckel och user_id som värde
            user_data = {"Name": user_id}

            # Kryptera användardata (konvertera till sträng innan kryptering)
            encrypted_data = encrypt_data(str(user_data))

            # Lägg till den nya krypterade användardatan i listan
            admin_users.append(encrypted_data)

            # Skriv krypterad data till .md-filen
            write_to_md_file(admin_users, ADMIN_FILE)


# create_admin("ArvidAlund")

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

        print(payload)
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

        print("get user by jwt users: ", users)

        for user in users:
            try:
                user_fields = user.split(", ")

                user_id = user_fields[0].split(": ")[1]
                user_name = user_fields[1].split(": ")[1]
                user_psw = user_fields[2].split(": ")[1]
                user_tier = user_fields[3].split(": ")[1]
                user_email = user_fields[4].split(": ")[1]

                # Ta bort ']' om det finns i e-postadressen
                if user_email.endswith("]"):
                    user_email = user_email[:-1]  # Ta bort sista tecknet

                # Ta bort eventuellt '"' från slutet av e-postadressen
                if user_email.endswith('"'):
                    user_email = user_email[:-1]

                firstname = None  # Defaultvärde om firstname inte finns
                lastname = None  # Defaultvärde om lastname inte finns

                # Försök hämta firstname om det finns
                if len(user_fields) > 5:
                    firstname = user_fields[5].split(": ")[1]

                # Försök hämta lastname om det finns
                if len(user_fields) > 6:
                    lastname = user_fields[6].split(": ")[1]

                if lastname.endswith("]"):
                    lastname = lastname[:-1]

                if lastname.endswith('"'):
                    lastname = lastname[:-1]

                if user_name == username:
                    # Returnera användardatan, inkludera firstname och lastname endast om de finns
                    user_data = {
                        "id": user_id,
                        "name": user_name,
                        "email": user_email,
                        "password": user_psw,
                        "tier": user_tier,
                        "firstname": "",
                        "lastname": "",
                    }

                    # Lägg till firstname och lastname om de finns
                    if firstname:
                        user_data["firstname"] = firstname
                    if lastname:
                        user_data["lastname"] = lastname

                    print(user_data, user_email)
                    return user_data
            except Exception as e:
                print(f"Fel vid bearbetning av användardata: {str(e)}")
                continue

        # Om ingen användare matchar
        print("Ingen användare matchade det angivna användarnamnet.")
        return None

    except Exception as e:
        print(f"Fel vid bearbetning av JWT-token: {str(e)}")
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

    for user in users:
        # Dela upp användardatan för att få ut användarnamn och tier
        user_fields = user.split(", ")
        user_name = user_fields[1].split(": ")[1]  # Extract 'Name' field
        user_tier = user_fields[3].split(": ")[1]  # Extract 'Tier' field
        user_id = user_fields[0].split(": ")[1]  # Extract 'UserID' field

        # Om användaren matchar den från token, uppdatera tier
        if user_name == username_from_token:
            user_found = True
            updated_user_data = f"UserID: {user_id}, username: {user_name}, password: {user_fields[2].split(': ')[1]}, Tier: {new_tier}, mail: {user_fields[4].split(': ')[1]}"
            updated_data.append(
                updated_user_data
            )  # Lägg till den uppdaterade användaren
            print(f"Användare uppdaterad: {updated_user_data}")
        else:
            updated_data.append(user)  # Lägg till användaren utan ändringar

    if not user_found:
        return jsonify({"message": "Användare ej hittad"}), 404

    # Kryptera den uppdaterade användardatan
    encrypted_data = encrypt_data(
        updated_data
    )  # Här krypteras hela listan av användardata

    # Skriv tillbaka den uppdaterade och krypterade användardatan i filen
    write_to_md_file(
        [encrypted_data], DATA_FILE
    )  # Skicka listan av krypterade strängar

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

    print("Namn: ", customerName, "Mail: ", customerEmail)

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


@app.route("/get_info_profile", methods=["POST"])
def get_info_profile():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"message": "Ingen autentisering tillhandahölls."}), 403
    token = auth_header.split(" ")[1]
    data = get_user_by_jwt(token)
    return data


if __name__ == "__main__":
    app.run(debug=False, port=5000)


# if "user" not in session:
#     return redirect(url_for("login"))

# PP = privatperson PA = Professionell användare FA = Företagsanvändare
