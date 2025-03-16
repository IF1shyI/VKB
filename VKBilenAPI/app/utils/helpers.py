import json
from app.models import db
import datetime

date = ""


def verify_api_key(api_key):
    with open("keys.md", "r") as file:
        api_keys = [json.loads(line)["api_key"] for line in file]
    return api_key in api_keys


def search_by_regnumber(regnummer, filename):
    try:
        with open(filename, "r") as file:
            car_data = json.load(file)

        for vehicle_type in car_data:
            # Search for reg in the list of vehicles for each type
            result = next(
                (car for car in car_data[vehicle_type] if car.get("reg") == regnummer),
                None,  # Return None if not found
            )
            if result:
                return result  # Return the matching vehicle if found

        return None  # Return None if regnummer is not found in any vehicle type

    except FileNotFoundError:
        return None  # Return None if file is not found


import json


import json


def save_to_json(data, filename):
    try:
        with open(filename, "r") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Om filen inte finns eller är tom, skapa en grundstruktur
        existing_data = {}

    # Hämta typen från data
    vehicle_type = data["type"]

    # Om den typen inte finns i den befintliga datan, skapa en ny lista för den typen
    if vehicle_type not in existing_data:
        existing_data[vehicle_type] = []

    # Lägg till det nya fordonet till rätt lista
    existing_data[vehicle_type].append(data)

    # Skriv tillbaka den uppdaterade datan till filen
    with open(filename, "w") as file:
        json.dump(existing_data, file, indent=4)


def extract_value_by_label(tree, label_text):
    # XPath för att hitta label och matcha den med texten
    label_xpath = f'//span[@class="label" and contains(text(), "{label_text}")]/following-sibling::span[@class="value"]/text()'

    # Hitta och returnera värdet
    value = tree.xpath(label_xpath)
    return value[0] if value else None


def calc_totsum(data):
    tot_sum = data["monthly_tax"] + data["maintenance"][0] + data["insurance"]


async def today_fuelprice(data):
    global date
    today = datetime.datetime.today().date()
    if date == today:
        if data["fuel_type"][0] == "Bensin":
            data["fuel_price"] = 15.5

        elif data["fuel_type"][0] == "Diesel":
            data["fuel_price"] = 16.7

        elif data["fuel_type"][0] == "Etanol":
            data["fuel_price"] = 13.2

    else:
        date = today

        if data["fuel_type"][0] == "Bensin":
            data["fuel_price"] = 15.5

        elif data["fuel_type"][0] == "Diesel":
            data["fuel_price"] = 16.7

        elif data["fuel_type"][0] == "Etanol":
            data["fuel_price"] = 13.2
