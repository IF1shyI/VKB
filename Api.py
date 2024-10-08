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
import time

# http://127.0.0.1:5000/bilinfo?reg_plate=CWJ801

app = Flask(__name__)
CORS(app)

# Ladda miljövariabler från .env-filen
load_dotenv()

# Hämta användarnamn och lösenord från miljövariabler
USERNAME = os.getenv("USERN")
PASSWORD = os.getenv("PASSWORD")

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
    print(text_without_liter)
    try:
        value = float(text_without_liter)
    except ValueError:
        # Om konverteringen misslyckas, kan du hantera det på ett lämpligt sätt
        value = None

    return value


# Funktion för att logga in och spara sessionen
def login_and_save_session(playwright):
    if USERNAME != None or PASSWORD != None:
        browser = playwright.chromium.launch(
            headless=True
        )  # Sätt till True om du vill köra i bakgrunden
        context = browser.new_context()

        page = context.new_page()

        # Gå till inloggningssidan
        page.goto("https://auth.car.info/sv-se?cachereset")

        # Klicka för att använda användarnamn och lösenord
        page.get_by_role("button", name="--> Användarnamn och lösenord").click()

        # Fyll i användarnamn och lösenord
        page.get_by_placeholder("Användarnamn eller E-post").fill(USERNAME)
        page.get_by_placeholder("Lösenord").fill(PASSWORD)

        # Klicka på "Logga in"-knappen
        page.get_by_role("button", name="Logga in").click()

        # Vänta på att inloggningen ska lyckas (letar efter "Logga ut"-knappen)
        page.wait_for_selector("text=Arvid Ålund", timeout=10000)

        # Kontrollera att inloggningen lyckades
        if page.is_visible("text=Arvid Ålund"):
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

        print("Hämtar Bensin förbrukning")
        bbruk_class = page.query_selector_all(".idva_float")
        for bbruk in bbruk_class:
            bbruk_pre = bbruk.inner_text()
            if bbruk_pre.endswith("100km"):
                global_besbruk = convert_text_to_float(bbruk_pre)
                print(bbruk_pre)
                break
            else:
                global_besbruk = "Ingen forbrukning hittad"

        print("Hämtar Fordonsskatt")
        fskatt_class = page.query_selector_all(".button-like")
        for skatt in fskatt_class:
            skatt_pre = skatt.query_selector(".btn_value")
            if skatt_pre:
                fskatt_pre = skatt_pre.inner_text()
                global_fskatt = convert_currency_text_to_int(fskatt_pre)

        print("Hämtar drivmedel")
        fskatt_class = page.query_selector_all(".idva_float")
        for text in fskatt_class:
            dmedel = text.inner_text()
            if dmedel.startswith("Diesel") or dmedel.startswith("Bensin"):
                drivmedel = dmedel
                break

        print("Hämtar co2 utsläpp")
        co2_class = page.query_selector_all(".idva_float")
        for text in co2_class:
            co2_name = text.inner_text()
            print(co2_name)
            if co2_name.endswith("g/km"):
                co2 = int(
                    co2_name.replace("\u00a0", "")
                    .replace("g/km", "")
                    .replace(",", ".")
                    .replace(" ", "")
                    .strip()
                )
                break

        # Stäng webbläsaren
        context.close()

        print(co2)
        return page_content


# Flask-routen som tar emot registreringsnumret och hämtar bilinformation
@app.route("/bilinfo", methods=["GET"])
@cache.cached(timeout=120, query_string=True)
def get_car_info():
    global global_car_model

    # Hämta registreringsnumret från query parameter
    reg_plate = request.args.get("reg_plate")

    if not reg_plate:
        return jsonify({"error": "No registration plate provided"}), 400

    # Hämta sidan via Playwright
    page_content = get_car_info_with_playwright(reg_plate)

    if page_content is None:
        return jsonify({"error": "Could not retrieve data"}), 500

    # Analysera HTML-innehållet med BeautifulSoup
    soup = BeautifulSoup(page_content, "html.parser")

    # Hämta bilmodell genom att leta efter <a> inuti <h1>
    h1_tag = soup.find("h1")

    if h1_tag == "Kaffepaus":
        return jsonify({"Försök igen senare"})
    car_model = (
        h1_tag.find("a").text.strip()
        if h1_tag and h1_tag.find("a")
        else "No model found"
    )

    global_car_model = car_model

    # Om ingen Fordonsskatt hittas, returnera en grundläggande modellinfo
    if h1_tag and h1_tag.text.strip() == "Kaffepaus":
        return jsonify({"message": "Try again later"})
    else:
        return jsonify(
            {
                "reg_plate": reg_plate,
                "car_model": car_model,
                "besbruk": global_besbruk,
                "fskatt": global_fskatt,
                "drivmedel": drivmedel,
                "Co2_bruk": co2,
            }
        )


@app.route("/fuel-prices", methods=["GET"])
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
        return jsonify({"petrolPrice": petrol_price, "dieselPrice": diesel_price})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Funktion som körs när applikationen stängs av
def on_shutdown():
    if os.path.exists(SESSION_FILE):
        print("Raderar session.json eftersom applikationen stängs av...")
        os.remove(SESSION_FILE)


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

Datum: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        # Definiera filnamn och filväg
        file_name = f"contact_{int(datetime.datetime.now().timestamp())}.md"
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


@app.route("/insurance", methods=["GET"])
def get_insurance():
    try:
        # Anropa funktionen för att hämta försäkringsdata
        with sync_playwright() as p:
            average_price = insurance(p)  # Skicka in playwright-instans

        # Kontrollera om medelpriset är None
        if average_price is None:
            return jsonify({"error": "Could not calculate average price"}), 400

        # Beräkna månadskostnaden
        average_price_month = average_price / 12

        # Returnera den beräknade månadskostnaden som JSON
        return jsonify({"average_price_month": average_price_month})

    except Exception as e:
        # Fångar oväntade fel och returnerar ett felmeddelande
        return jsonify({"error": str(e)}), 500


def insurance(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Gå till inloggningssidan
    page.goto("https://copilot.microsoft.com/?msockid=2703ee02556e635a1eb6fc6a54466276")

    # Vänta på att textarea ska laddas
    page.wait_for_selector("#searchbox")

    # Skriv in text i textarea
    page.fill(
        "#searchbox",
        f"Vad är det genomsnittliga priset för en helförsäkring för en {global_car_model} i svenska kronor? Svara endast med ett heltal utan några skiljetecken (t.ex. mellanslag eller kommatecken), och ge inga förklaringar eller annan text.",
    )

    # Tryck på Enter-tangenten
    page.press("#searchbox", "Enter")

    # Vänta på att elementet med klassen 'tooltip-target' ska laddas
    time.sleep(5)

    # Hämta texten från elementet med klassen 'tooltip-target'
    average_price_ai = int(page.inner_text(".ac-textBlock"))

    print("Svaret från AI:", average_price_ai)

    # Stäng webbläsaren
    context.close()
    browser.close()

    # Kontrollera att average_price inte är None innan du returnerar
    if average_price_ai is not None:
        return average_price_ai  # Returnera medelpriset som ett tal
    else:
        return None  # Hantera fallet där siffror inte kunde extraheras korrekt


@app.route("/maintenance", methods=["GET"])
def get_maintenance():
    try:
        # Anropa funktionen för att hämta försäkringsdata
        with sync_playwright() as p:
            maintenance_data = maintenance(p)  # Skicka in playwright-instans

        # Kontrollera om medelpriset är None
        if maintenance_data is None:
            return jsonify({"error": "Could not calculate average price"}), 400
        # Skapa en JSON-struktur där varje del separeras

        # Kontrollera att data är en lista med tuples
        if not isinstance(maintenance_data, list) or not all(
            isinstance(item, tuple) and len(item) == 2 for item in maintenance_data
        ):
            return jsonify({"error": "Invalid maintenance data format"}), 400

        response_data = {}

        for item in maintenance_data:
            print("Item: ", item)
            category = item[0]  # T.ex. 'Service och reperationer'
            yearly_cost = item[1]  # T.ex. 666.67
            monthly_cost = (
                yearly_cost / 12
            )  # Dela årsbeloppet med 12 för att få månadskostnad

            # Lägg till månadskostnaden till svaret
            response_data[category] = round(monthly_cost, 2)

        # Returnera som JSON
        return jsonify(response_data)

    except Exception as e:
        # Fångar oväntade fel och returnerar ett felmeddelande
        return jsonify({"error": str(e)}), 500


def maintenance(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Gå till inloggningssidan
    page.goto("https://copilot.microsoft.com/?msockid=2703ee02556e635a1eb6fc6a54466276")

    # Vänta på att textarea ska laddas
    page.wait_for_selector("#searchbox")

    # Skriv in text i textarea
    page.fill(
        "#searchbox",
        f"vad är det genomsnitliga priset för underhåll på en {global_car_model} i svenska kronor? Svara endast med ett heltal utan några skiljetecken (t.ex. mellanslag eller kommatecken), och ge inga förklaringar eller annan text. Dela upp svaret i 'Service och reperationer'', 'Däckbyte och underhåll'",
    )

    # Tryck på Enter-tangenten
    page.press("#searchbox", "Enter")

    # Vänta på att elementet med klassen 'tooltip-target' ska laddas
    time.sleep(8)

    # Hämta texten från elementet med klassen 'tooltip-target'
    maintenancecost = page.inner_text(".ac-textBlock")

    print("Svaret från AI:", maintenancecost)

    # Stäng webbläsaren
    context.close()
    browser.close()

    matches = re.findall(r"([a-zA-ZåäöÅÄÖ\s]+):\s*(\d+)", maintenancecost)

    # Konvertera till lista
    resultat_lista = [(item[0].strip(), int(item[1])) for item in matches]

    print(resultat_lista)
    # Kontrollera att average_price inte är None innan du returnerar
    if resultat_lista is not None:
        return resultat_lista  # Returnera medelpriset som ett tal
    else:
        return None  # Hantera fallet där siffror inte kunde extraheras korrekt


# Registrera funktionen för att köra vid avslut
atexit.register(on_shutdown)

if __name__ == "__main__":
    app.run(debug=True)
