from lxml import html
from app.utils.extract_car_info import extract_car_info
from dotenv import load_dotenv
import os

load_dotenv()

SCRAPERAPI_KEY = os.getenv("SCRAPERAPI_KEY")
BASE_URL = "https://www.biluppgifter.se/fordon/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}


async def fetch_data(session, reg_number):
    url = f"https://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}&url={BASE_URL}{reg_number}/"

    try:
        async with session.get(url, headers=HEADERS, timeout=10) as response:
            if response.status == 200:
                content = await response.text()
                print(f"\n==== HTML INNEHÅLL FÖR {reg_number} ====\n")

                # Använd lxml för att parsa HTML-innehållet
                tree = html.fromstring(content)

                # Extrahera relevant data från sidan
                car_info = extract_car_info(tree)

                print(f"Relevanta data för {reg_number}: {car_info}")
                return {
                    "regnr": reg_number,
                    "success": True,
                    "status": "Data hämtad",
                    "car_info": car_info,
                }
            else:
                print(f"\n[ERROR] {reg_number}: Statuskod {response.status}\n")
                return {"regnr": reg_number, "status": f"Fel {response.status}"}
    except Exception as e:
        print(f"\n[ERROR] {reg_number}: {str(e)}\n")
        return {"regnr": reg_number, "success": False, "status": f"Fel: {str(e)}"}
