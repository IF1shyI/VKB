from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from flask_caching import Cache
from playwright.sync_api import sync_playwright
import os
import atexit
from dotenv import load_dotenv
from flask_cors import CORS

# http://127.0.0.1:5000/bilinfo?reg_plate=CWJ801

app = Flask(__name__)
CORS(app)

# Ladda miljövariabler från .env-filen
load_dotenv()

# Hämta användarnamn och lösenord från miljövariabler
USERNAME = os.getenv("USERN")
PASSWORD = os.getenv("PASSWORD")

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
        value = "Hittade ej skatt"

    return value


def convert_text_to_float(text):
    # Ta bort unicode
    text_without_unicode = text.replace("\u00a0", "")

    # Ta bort "l/100km" från texten
    text_without_liter = text_without_unicode.replace("l/100km", "").strip()

    # Ersätta eventuella kommatecken om de finns
    text_without_liter = text_without_liter.replace(",", ".")
    print(text_without_liter)
    try:
        value = float(text_without_liter)
    except ValueError:
        # Om konverteringen misslyckas, kan du hantera det på ett lämpligt sätt
        value = None

    return value


# Funktion för att logga in och spara sessionen
def login_and_save_session(playwright):
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


# Funktion för att hämta bilinformation med Playwright, använder sparad session om den finns
def get_car_info_with_playwright(reg_plate):
    global global_besbruk
    global global_fskatt
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

        # Stäng webbläsaren
        context.close()

        return page_content


# Flask-routen som tar emot registreringsnumret och hämtar bilinformation
@app.route("/bilinfo", methods=["GET"])
@cache.cached(timeout=120, query_string=True)
def get_car_info():
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
            }
        )


# Funktion som körs när applikationen stängs av
def on_shutdown():
    if os.path.exists(SESSION_FILE):
        print("Raderar session.json eftersom applikationen stängs av...")
        os.remove(SESSION_FILE)


# Registrera funktionen för att köra vid avslut
atexit.register(on_shutdown)

if __name__ == "__main__":
    app.run(debug=True)
