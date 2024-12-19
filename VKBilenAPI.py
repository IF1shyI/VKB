from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from flask_caching import Cache
from playwright.sync_api import sync_playwright
import os
import atexit
from dotenv import load_dotenv
from flask_cors import CORS
import datetime
import re
from openai import OpenAI
from flask_session import Session
from datetime import datetime
import requests
import hashlib
import json


# http://127.0.0.1:4000/bilinfo?reg_plate=CWJ801

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
global_besbruk = "Error"
global_fskatt = "Error"
drivmedel = "Error"
co2 = "Error"

CAR_FILE = "cardata.md"

# Använd serverbaserade sessioner (sessioner som sparas på servern)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SECURE"] = False

Session(app)


def save_to_json(data, filename="car_costs.json"):
    try:
        # Läsa in befintlig data från JSON-filen
        try:
            with open(filename, "r") as file:
                car_data = json.load(file)
        except FileNotFoundError:
            car_data = {"bilar": []}  # Om filen inte finns, skapa en ny struktur

        # Lägg till ny bilinformation i listan
        car_data["bilar"].append(data)

        # Spara den uppdaterade datan till fil
        with open(filename, "w") as file:
            json.dump(car_data, file, indent=4)
    except Exception as e:
        print(f"Error saving data to JSON: {e}")


def read_from_json(filename="car_costs.json"):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"bilar": []}
    except Exception as e:
        print(f"Error reading data from JSON: {e}")
        return {"bilar": []}


def search_by_regnumber(regnummer, filename="car_costs.json"):
    car_data = read_from_json(filename)
    for car in car_data["bilar"]:
        if car["regnummer"] == regnummer:
            return car
    return None


# Funktion för att skapa en hash av API-nyckeln
def create_api_key(user_name):
    # Skapa en unik API-nyckel genom att kombinera användarnamn och nuvarande tid
    raw_key = f"{user_name}-{datetime.now().timestamp()}".encode("utf-8")

    # Skapa SHA256 hash av den råa nyckeln
    hashed_key = hashlib.sha256(raw_key).hexdigest()

    return raw_key.decode("utf-8"), hashed_key


# Funktion för att lägga till både råa och hashade nycklar till .md-filen
def add_api_key_to_file(user_name, hashed_key, file_path="api_keys.md"):
    # Skapa en beskrivning för användaren och nyckeln
    entry = f"## User: {user_name}\n"
    entry += f"- **API Key (Hashed)**: {hashed_key}\n"
    entry += f"- **Created on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Skriv till filen
    with open(file_path, "a") as file:
        file.write(entry)

    print(f"Ny API-nyckel för {user_name} har lagts till i filen.")


def verify_api_key(input_key, file_path="api_keys.md"):
    # Kontrollera om input_key är None eller tom
    if not input_key:
        print("API key is missing or invalid.")
        return False

    # Hasha input-nyckeln
    hashed_input_key = hashlib.sha256(input_key.encode("utf-8")).hexdigest()

    try:
        with open(file_path, "r") as file:
            # Läs filen rad för rad
            lines = file.readlines()

        # Iterera över rader och sök efter hashad nyckel
        for line in lines:
            if "API Key (Hashed)" in line and hashed_input_key in line:
                print("API key is valid.")
                return True

        print("Invalid API key.")
        return False

    except FileNotFoundError:
        print("API key file not found.")
        return False


# Funktion för att läsa och uppdatera API-nyckelns förfrågningar
def update_api_request_count(api_key, file_path="api_requests.md"):
    current_date = datetime.now()
    current_month = current_date.strftime("%Y-%m")

    # Läs in filen och kolla om nyckeln redan finns
    api_data = {}
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            content = file.readlines()
            user_key = None
            requests_made = 0
            last_reset = None

            # Hitta rätt nyckel och uppdatera
            for line in content:
                if f"API Key: {api_key}" in line:
                    user_key = api_key
                    requests_made = int(line.split("Requests Made: ")[1].split("\n")[0])
                    last_reset = line.split("Last Reset: ")[1].strip()
                    break

            # Om vi hittar användaren, öka antalet förfrågningar
            if user_key:
                requests_made += 1
                # Uppdatera data för användaren
                api_data[user_key] = {
                    "requests_made": requests_made,
                    "last_reset": last_reset,
                }
            else:
                # Om nyckeln inte finns, skapa en ny
                api_data[api_key] = {"requests_made": 1, "last_reset": current_month}

    else:
        # Om filen inte existerar, skapa en ny
        api_data[api_key] = {"requests_made": 1, "last_reset": current_month}

    # Skriv tillbaka till filen
    with open(file_path, "w") as file:
        for key, data in api_data.items():
            file.write(f"## User: {key}\n")
            file.write(f"- **API Key**: {key}\n")
            file.write(f"- **Requests Made**: {data['requests_made']}\n")
            file.write(f"- **Last Reset**: {data['last_reset']}\n\n")


# Funktion för att nollställa förfrågningar varje månad
def reset_request_counts(file_path="api_requests.md"):
    current_date = datetime.now()
    current_month = current_date.strftime("%Y-%m")

    # Läs filen och kontrollera om det är dags att nollställa
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            content = file.readlines()

        updated_content = []
        reset_needed = False

        # Iterera över varje användare och kolla om det är en ny månad
        for line in content:
            if "Last Reset" in line:
                last_reset = line.split("Last Reset: ")[1].strip()
                if last_reset != current_month:
                    reset_needed = True
                    updated_content.append(line.replace(last_reset, current_month))
                else:
                    updated_content.append(line)
            else:
                updated_content.append(line)

        if reset_needed:
            # Om vi nollställer, skriv tillbaka filen med nollade förfrågningar
            with open(file_path, "w") as file:
                for line in updated_content:
                    if "Requests Made" in line:
                        file.write(
                            line.replace(line.split(": ")[1].split("\n")[0], "0")
                        )
                    else:
                        file.write(line)


def convert_currency_text_to_int(text):
    # Ta bort unicode
    text_without_unicode = text.replace("\u00a0", "")

    # Ta bort "SEK" från texten
    text_without_currency = text_without_unicode.replace("SEK", "").strip()

    # Ersätta eventuella kommatecken om de finns (om texten är "1,234 SEK")
    text_without_currency = text_without_currency.replace(",", "")

    # Konvertera den återstående texten till ett heltal
    try:
        value = int(text_without_currency)
    except ValueError:
        # Om konverteringen misslyckas, kan du hantera det på ett lämpligt sätt
        value = 0

    return value


def convert_text_to_float(text):
    # Ta bort unicode
    text_without_unicode = text.replace("\u00a0", "")

    # Ta bort "l/100km" från texten
    text_without_liter = text_without_unicode.replace("l/100km", "").strip()

    # Ersätta eventuella kommatecken om de finns
    text_without_liter = text_without_liter.replace(",", ".")
    text_without_liter = text_without_liter.replace(" ", "")
    try:
        value = float(text_without_liter)
    except ValueError:
        # Om konverteringen misslyckas, kan du hantera det på ett lämpligt sätt
        value = None

    return value


# Funktion för att logga in och spara sessionen
def login_and_save_session(playwright):
    if USERNAME != None or PASSWORD != None:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://auth.car.info/sv-se?cachereset")

        page.get_by_role("button", name="Användarnamn och lösenord").click()
        page.get_by_placeholder("Användarnamn eller E-post").click()
        page.get_by_placeholder("Användarnamn eller E-post").fill(USERNAME)

        page.get_by_placeholder("Lösenord").click()
        page.get_by_placeholder("Lösenord").fill(PASSWORD)

        page.get_by_role("button", name="Logga in").click()

        # Vänta på att inloggningen ska lyckas (letar efter "Logga ut"-knappen)
        page.wait_for_selector("#main_header", timeout=10000)

        # Kontrollera att inloggningen lyckades
        if page.is_visible("text=Mina listor"):
            print("Inloggningen lyckades!")

            # Spara sessionen till en fil
            context.storage_state(path=SESSION_FILE)
        else:
            print("Inloggningen misslyckades!")

        # Stäng webbläsaren
        context.close()
        browser.close()
    else:
        print("Inga inloggningsdetaljer")


# Funktion för att hämta bilinformation med Playwright, använder sparad session om den finns
def get_car_info_with_playwright(reg_plate):
    global global_besbruk
    global global_fskatt
    global drivmedel
    global co2
    with sync_playwright() as p:
        # Kolla om sessionen redan är sparad
        if os.path.exists(SESSION_FILE):
            print("Laddar tidigare session...")
            # Använd sparad session
            context = p.chromium.launch(headless=True).new_context(
                storage_state=SESSION_FILE
            )
        else:
            print("Ingen sparad session, loggar in och sparar sessionen...")
            # Logga in och spara sessionen
            login_and_save_session(p)
            # Skapa ett nytt kontext med den nyligen sparade sessionen
            context = p.chromium.launch(headless=True).new_context(
                storage_state=SESSION_FILE
            )

        page = context.new_page()

        # Navigera till bilens informationssida med registreringsnumret
        page.goto(f"https://www.car.info/sv-se/license-plate/S/{reg_plate}")

        # Vänta på att sidan med bilinformation ska laddas
        page.wait_for_selector("h1", timeout=10000)  # Vänta tills <h1> finns på sidan

        # Få HTML-innehållet för bilens informationssida
        page_content = page.content()

        col3_class = page.query_selector_all(
            ".col-md-3"
        )  # Hämtar alla element med klassen col-md-3
        for div_element in col3_class:

            div_content = div_element.text_content().strip()  # Hämta textinnehållet
            if (
                "Blandad förbrukning" in div_content
            ):  # Kontrollera om texten innehåller "Blandad förbrukning"

                # Hämta specifik information från den inre div med klassen "idva_float"
                div_bbruk = div_element.query_selector(
                    ".idva_float"
                )  # OBS! query_selector används här, inte _all
                if div_bbruk:  # Kontrollera om elementet hittades
                    besbruk_pre = div_bbruk.text_content().strip()
                    if besbruk_pre.endswith("100km"):
                        global_besbruk = convert_text_to_float(besbruk_pre)

                        break
                else:
                    global_besbruk = "Ingen förbrukning hittad"

        fskatt_class = page.query_selector_all(".featured_info_item")
        for item in fskatt_class:
            div_elements = item.query_selector_all(".btn_description")
            for div in div_elements:
                div_text = div.text_content().strip()  # Extrahera och trimma texten

                if div_text == "Fordonsskatt":

                    fskatt_pre = item.query_selector(".btn_value").inner_text()
                    global_fskatt = convert_currency_text_to_int(fskatt_pre)

        fskatt_class = page.query_selector_all(".idva_float")
        for text in fskatt_class:
            dmedel = text.inner_text()
            if dmedel.startswith("Diesel") or dmedel.startswith("Bensin"):
                drivmedel = dmedel
                break

        co2_class = page.query_selector_all(".has_extra_info_modal")
        for text in co2_class:
            co2_name = (
                text.inner_text().strip()
            )  # Rensa strängen från mellanslag i början och slutet
            if co2_name.endswith("g/km"):

                # Extrahera endast siffror följt av "g/km"
                match = re.search(r"(\d+)\s*g/km", co2_name)
                if match:
                    try:
                        co2 = int(match.group(1))  # Extrahera siffran från matchningen

                    except ValueError as e:
                        print(f"Fel vid konvertering av {repr(co2_name)}: {e}")
                else:
                    print("Ingen giltig CO₂-data hittades:", repr(co2_name))
                    break

        if co2 == "Error":
            co2 = 130

        # Stäng webbläsaren
        context.close()

        return page_content


def contact_ai(promt):

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": promt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    return response


# Underhåll
def maintenance():

    maintenance_prompt = f"""
        What is the average annual maintenance cost for a {global_car_model} in Swedish kronor?
        Please provide only an integer for each category without any delimiters (e.g., spaces or commas), 
        and offer only the amount with no additional explanations.

        For the following:
        - Maintenance (service, oil changes, etc.): [Enter amount]
        - Tire replacement cost: [Enter amount]
        - Other repairs (brake pads, etc.): [Enter amount]

        Please only return the amounts for the above categories, and DO NOT include any total or summary information.
        """
    response = contact_ai(maintenance_prompt)

    maintenancecost = response.choices[0].message.content

    # Använd regex för att hitta alla siffror i 'content'
    # Hitta innehåll inom 'content'

    if maintenancecost:
        # Extrahera alla siffror från innehållet
        nested_list = []
        for line in maintenancecost.strip().split("\n"):
            if ":" in line:
                # Dela upp titeln och beloppet vid det första kolon, hantera mellanrum noggrant
                title, amount = line.split(
                    ":", 1
                )  # '1' gör att vi bara delar på första kolon
                try:
                    nested_list.append(
                        [
                            title.strip().replace(" ", ""),
                            int(amount.strip().replace(" ", "")),
                        ]
                    )  # Ta bort mellanrum från beloppet
                except ValueError:
                    # Om omvandlingen till int misslyckas (t.ex. om beloppet inte är ett heltal)
                    print(f"Fel vid omvandling av belopp på raden: '{line}'")
                    continue

    else:
        print("Hittade inget matchande innehåll.")
    if not nested_list:
        print("Ingen giltig data extraherades. Försök igen.")
        return maintenance()

    # Skriv ut det genererade svaret

    # Kontrollera att average_price inte är None innan du returnerar
    if nested_list is not None:
        return nested_list  # Returnera medelpriset som ett tal
    else:
        return None  # Hantera fallet där siffror inte kunde extraheras korrekt


# år till månad
def calculate_monthly_costs(data):

    month_cost = int(data / 12)

    return month_cost


# Försäkring
# Tar reda på kostnad per månad
def get_insurance():
    """
    Hämtar den genomsnittliga årliga kostnaden för en omfattande bilförsäkring för en specifik bilmodell.

    Skickar en fråga till OpenAI:s GPT-3.5-modell för att få försäkringskostnaden och beräknar därefter
    månadskostnaden baserat på det årliga priset. Om något fel uppstår under processen, returneras ett
    felmeddelande.

    Returns:
    float: Månadskostnaden för försäkringen i svenska kronor, eller ett felmeddelande i JSON-format vid problem.

    Felhantering:
    - Vid fel i API-anrop eller bearbetning av svar, returneras ett felmeddelande med statuskod 500.
    - Om det inte går att beräkna ett giltigt pris, returneras ett felmeddelande med statuskod 400.
    """
    try:

        insurance_prompt = f"What is the average yearly cost of comprehensive insurance for a {global_car_model} in Swedish kronor? Provide the yearly total as a single integer, formatted without spaces, commas, or other delimiters. Do not include any explanations or additional text."

        response = contact_ai(insurance_prompt)
        average_price = response.choices[0].message.content
        # Använd regex för att hitta innehållet i 'content'
        average_price = int(average_price)
        if average_price is None:
            average_price = 0
            return jsonify({"error": "Could not calculate average price"}), 400

        if average_price != 0:
            # Beräkna månadskostnaden
            average_price_month = average_price / 12
        else:
            average_price_month = 0

        # Returnera den beräknade månadskostnaden som JSON
        return average_price_month

    except Exception as e:
        # Fångar oväntade fel och returnerar ett felmeddelande
        print("Ett fel uppstod:", e)
        return jsonify({"error": str(e)}), 500


# Dagens bensinkostnader
def get_fuel_prices():
    try:
        # Starta Playwright-webbläsaren
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Gå till Preem-sidan för drivmedelspriser
            page.goto("https://www.preem.se/privat/drivmedel/drivmedelspriser/")

            # Hämta bensinpris (95 oktan) och dieselpris från tabellen
            petrol_price_text = (
                page.locator("table")
                .locator("text=95")
                .first.locator("..")
                .locator("td:nth-child(2)")
                .inner_text()
            )
            diesel_price_text = (
                page.locator("table")
                .locator("text=Diesel")
                .first.locator("..")
                .locator("td:nth-child(2)")
                .inner_text()
            )

            # Konvertera prissträngar till flyttal
            petrol_price = float(
                petrol_price_text.replace("kr/l", "").replace(",", ".").strip()
            )
            diesel_price = float(
                diesel_price_text.replace("kr/l", "").replace(",", ".").strip()
            )

            browser.close()

        # Returnera priserna som JSON
        return {"petrolPrice": petrol_price, "dieselPrice": diesel_price}

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_electricity_price(year, month, day, price_class="SE3"):
    """
    Hämtar elpriser från API:t på elprisetjustnu.se baserat på angivet datum och prisklass.

    Parametrar:
    - year (int): Året för elpriserna (t.ex. 2024).
    - month (int): Månaden för elpriserna (t.ex. 12).
    - day (int): Dagen för elpriserna (t.ex. 18).
    - price_class (str): Prisklass, standard är "SE3", kan ändras till andra prisklasser.

    Returvärde:
    - dict: En dictionary med elpriser om det lyckas, annars None.
    """
    # Formatera datum och skapa URL
    date_str = (
        f"{year}-{month:02d}-{day:02d}"  # Skapar datumsträng i formatet ÅR-MÅNAD-DAG
    )
    url = f"https://www.elprisetjustnu.se/api/v1/prices/{year}/{month:02d}-{day:02d}_{price_class}.json"

    try:
        # Skicka GET-förfrågan till API:t
        response = requests.get(url)
        response.raise_for_status()  # Om förfrågan misslyckas, kasta ett undantag

        # Om API:t ger ett resultat, returnera data
        return response.json()

    except requests.exceptions.RequestException as e:
        # Hantera eventuella fel som uppstår vid API-anropet
        print(f"Fel vid hämtning av elpriser: {e}")
        return None


# Funktion som körs när applikationen stängs av
def on_shutdown():
    if os.path.exists(SESSION_FILE):
        print("Raderar session.json eftersom applikationen stängs av...")
        os.remove(SESSION_FILE)


def get_fuel_type(vehicle_info):
    """
    Identifierar bränsletypen för ett fordon baserat på en given sträng.

    Funktionen söker igenom fordonets information (sträng) för att avgöra om
    det använder bensin, diesel eller något annat bränsle.

    Parametrar:
    vehicle_info (str): En sträng som beskriver fordonet, t.ex. "Bensin | E85, 1.6 I4" eller
                         "Diesel (HVO100-kompatibel), 2.0 I4".

    Returvärde:
    str: Bränsletypen, antingen "Bensin", "Diesel" eller "Okänt" om ingen matchning finns.
    """
    # Matcha om "Bensin" eller "Diesel" finns i strängen
    if re.search(r"\bBensin\b", vehicle_info, re.IGNORECASE):
        return "Bensin"
    elif re.search(r"\bDiesel\b", vehicle_info, re.IGNORECASE):
        return "Diesel"
    else:
        return "Okänt"


def get_relative_fuelprice(allgasprice, fuel_type):
    if fuel_type == "Diesel":
        return allgasprice["dieselPrice"]
    if fuel_type == "Bensin":
        return allgasprice["petrolPrice"]
    if fuel_type == "El":
        today = datetime.today()
        prices = get_electricity_price(today.year, today.month, today.day)
        if prices:
            print(f"Dagens elpriser: {prices}")
        else:
            return "Could not get power price"


def get_tire_cost(data):
    tire_month = data / 48

    int_tire_month = int(tire_month)

    return int_tire_month


def calc_tot_cost(insurance, fskatt, maintenance):
    month_tax = fskatt / 12
    int_month_tax = int(month_tax)

    tot_cost = insurance + int_month_tax + maintenance

    return tot_cost


# Mainfunktion
@app.route("/carcost", methods=["GET"])
def car_cost_month():
    reg_plate = request.args.get("reg_plate")
    api_key = request.args.get("key")
    is_valid = verify_api_key(api_key)

    if is_valid:
        existing_car = search_by_regnumber(reg_plate)
        if existing_car:
            update_api_request_count(api_key)
            return jsonify(existing_car)

        # Fetch car info using Playwright
        try:
            page_content = get_car_info_with_playwright(reg_plate)
            if page_content is None:
                return jsonify({"error": "Could not retrieve data"}), 500
        except Exception as e:
            return jsonify({"error": f"Failed to fetch car data: {str(e)}"}), 500

        # Process car information using BeautifulSoup
        soup = BeautifulSoup(page_content, "html.parser")
        h1_tag = soup.find("h1")

        if not h1_tag or h1_tag.text.strip() == "Kaffepaus":
            return jsonify({"error": "Try again later or invalid vehicle info"}), 400

        car_model = (
            h1_tag.find("a").text.strip() if h1_tag.find("a") else "No model found"
        )
        global global_car_model
        global_car_model = car_model

        # Fetch maintenance data
        try:
            maintenance_data = maintenance()
            if not maintenance_data:
                return jsonify({"error": "Could not retrieve maintenance data"}), 400
        except Exception as e:
            return (
                jsonify({"error": f"Failed to fetch maintenance data: {str(e)}"}),
                500,
            )

        # Calculate maintenance costs
        tirecost = get_tire_cost(maintenance_data[1][1])
        maintenance_month = calculate_monthly_costs(maintenance_data[0][1])
        repairs_month = calculate_monthly_costs(maintenance_data[2][1])
        tot_maintenance = repairs_month + maintenance_month + tirecost

        # Calculate tax costs
        tax_month = calculate_monthly_costs(global_fskatt)

        # Fetch insurance data
        try:
            insurance = get_insurance()
        except Exception as e:
            return jsonify({"error": f"Failed to fetch insurance data: {str(e)}"}), 500

        # Fetch fuel prices
        try:
            gasprice = get_fuel_prices()
            fuel_type = get_fuel_type(drivmedel)
            right_fuel_price = get_relative_fuelprice(gasprice, fuel_type)
        except Exception as e:
            return jsonify({"error": f"Failed to fetch fuel prices: {str(e)}"}), 500

        # Calculate total cost
        try:
            tot_cost = calc_tot_cost(insurance, tax_month, tot_maintenance)
            # Sammanställ data för den aktuella bilen
            car_info = {
                "regnummer": reg_plate,
                "total_cost": round(tot_cost),
                "tot_maintenance": round(tot_maintenance),
                "maintenance_month": round(maintenance_month),
                "repairs_month": round(repairs_month),
                "tirecost_month": round(tirecost),
                "insurance": round(insurance),
                "car_tax": round(tax_month),
                "car_name": global_car_model,
                "fuel_consumption": global_besbruk,
                "fuel_type": fuel_type,
                "fuel_price": right_fuel_price,
            }

            # Spara data till JSON
            save_to_json(car_info)
            update_api_request_count(api_key)

            return jsonify(car_info)

        except Exception as e:
            return jsonify({"error": f"Failed to calculate total cost: {str(e)}"}), 500
    else:
        return jsonify({"error": "Not a valid key"}), 401


@app.route("/create_api_key", methods=["POST"])
def create_key():
    # Ta emot användarnamnet från begäran
    user_name = request.json.get("user_name")

    if not user_name:
        return jsonify({"error": "user_name is required"}), 400

    # Skapa API-nyckeln
    raw_key, hashed_key = create_api_key(user_name)

    # Lägg till nyckeln till .md-filen
    add_api_key_to_file(user_name, hashed_key)

    # Returnera den råa och hashade nyckeln som svar
    return jsonify({"raw_key": raw_key}), 200


atexit.register(on_shutdown)


if __name__ == "__main__":
    app.run(debug=False, port=4000)


# user_name = "hej"  # Namn på användaren som ska få en ny nyckel
# raw_key, hashed_key = create_api_key(user_name)

# # Lägg till den råa och hashade nyckeln i filen
# add_api_key_to_file(user_name, raw_key, hashed_key)

# curl -X POST http://127.0.0.1:4000/create_api_key -H "Content-Type: application/json" -d '{"user_name": "example_user"}'
