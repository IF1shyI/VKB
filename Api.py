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
from openai import OpenAI

# http://127.0.0.1:5000/bilinfo?reg_plate=CWJ801

app = Flask(__name__)
CORS(app)

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
SESSION_FILE_AI = "sessionai.json"  # Fil för att lagra sessionen
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
        print(
            "All data: ",
            "reg_plate: ",
            reg_plate,
            "car_model: ",
            car_model,
            "besbruk: ",
            global_besbruk,
            "fskatt: ",
            global_fskatt,
            "drivmedel: ",
            drivmedel,
            "Co2_bruk: ",
            co2,
        )
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

        insurance_prompt = f"What is the average annual cost of comprehensive insurance for a {global_car_model} in Swedish kronor? Provide the yearly total as a single integer, formatted without spaces, commas, or other delimiters. Do not include any explanations or additional text."

        print("Prompten är:", insurance_prompt)
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": insurance_prompt,
                }
            ],
            model="gpt-3.5-turbo",
        )
        text = """ChatCompletion(id='chatcmpl-AUxRu5NKFprbkToVp8a7NdJ5JiTFn', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='6003', refusal=None, role='assistant', function_call=None, tool_calls=None))], created=1731941726, model='gpt-3.5-turbo-0125', object='chat.completion', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=2, prompt_tokens=74, total_tokens=76, prompt_tokens_details={'cached_tokens': 0, 'audio_tokens': 0}, completion_tokens_details={'reasoning_tokens': 0, 'audio_tokens': 0, 'accepted_prediction_tokens': 0, 'rejected_prediction_tokens': 0}))"""

        print(response)
        average_price = response.choices[0].message.content
        print("Genomsnittligt försäkringspris:", average_price)
        print("Svaret från ai: ", average_price)
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
        return jsonify({"average_price_month": average_price_month})

    except Exception as e:
        # Fångar oväntade fel och returnerar ett felmeddelande
        print("Ett fel uppstod:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/maintenance", methods=["GET"])
def get_maintenance():
    try:
        maintenance_data = maintenance()
        # Anropa funktionen för att hämta försäkringsdata
        # Kontrollera om medelpriset är None
        if maintenance_data is None:
            response_data = 0
            return jsonify({"error": "Could not calculate average price"}), 400

        def calculate_monthly_costs(yearly_costs, categories):
            response_data = {}

            # Loopar genom varje årsbelopp och kategori
            for index, (yearly_cost, category) in enumerate(
                zip(yearly_costs, categories)
            ):
                # Beräkna månadskostnaden
                monthly_cost = yearly_cost / 12

                # Lägg till månadskostnaden i response_data med kategorinamn
                response_data[category] = round(monthly_cost, 2)

            return response_data

        # Exempel på användning:
        categories = ["Service och reperationer", "Däckbyte och underhåll"]

        # Hämta månadskostnader
        result = calculate_monthly_costs(maintenance_data, categories)
        print(result)
        # Returnera som JSON
        return jsonify(result)

    except Exception as e:
        # Fångar oväntade fel och returnerar ett felmeddelande
        print("Ett fel uppstod:", e)
        return jsonify({"error": str(e)}), 500


def maintenance():

    maintenance_prompt = (
        f"What is the average maintenance cost for a {global_car_model} in Swedish kronor? "
        "Please respond only with an integer without any delimiters (e.g., spaces or commas), "
        "and provide no explanations or additional text.\n\n"
        "Specify the following:\n"
        "1. Service and repairs: [Enter amount]\n"
        "2. Tire change and maintenance: [Enter amount]\n"
    )

    print("Prompten är:", maintenance_prompt)

    text = """ChatCompletion(id='chatcmpl-AUxRvs041rJFGh1FgBNu5JxI5E2Lh', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='1. 6000\n2. 3000', refusal=None, role='assistant', function_call=None, tool_calls=None))], created=1731941727, model='gpt-3.5-turbo-0125', object='chat.completion', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=11, prompt_tokens=96, total_tokens=107, prompt_tokens_details={'cached_tokens': 0, 'audio_tokens': 0}, completion_tokens_details={'reasoning_tokens': 0, 'audio_tokens': 0, 'accepted_prediction_tokens': 0, 'rejected_prediction_tokens': 0}))"""
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": maintenance_prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )
    print(response)
    maintenancecost = response.choices[0].message.content

    print("Svaret från ai: ", maintenancecost)
    maintenancecost = int(maintenancecost)
    # Använd regex för att hitta alla siffror i 'content'
    # Hitta innehåll inom 'content'

    if maintenancecost:
        # Extrahera alla siffror från innehållet
        numbers = re.findall(
            r"\d+", maintenancecost[0]
        )  # Leta efter alla siffror i 'content'
        # Filtrera bort 1 och 2
        numbers = [int(num) for num in numbers if num not in ["1", "2"]]
    else:
        print("Hittade inget matchande innehåll.")
    print("Genererad data:", numbers)
    # Skriv ut det genererade svaret
    print("Service:", numbers[0], "\nMaintiance:", numbers[1])

    # Kontrollera att average_price inte är None innan du returnerar
    if numbers is not None:
        return numbers  # Returnera medelpriset som ett tal
    else:
        return None  # Hantera fallet där siffror inte kunde extraheras korrekt


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


# Registrera funktionen för att köra vid avslut
atexit.register(on_shutdown)

if __name__ == "__main__":
    app.run(debug=False)
