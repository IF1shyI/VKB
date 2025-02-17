import requests
import json
import os


def call_carinfo(reg_plate, language="sv"):
    id_lista = [1298, 540]

    url = f"https://api.car.info/v2/app/demo/license-plate/S/{reg_plate}"

    headers = {"Accept": "application/json", "Accept-Language": language}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Kastar ett fel om statuskoden inte är 200

        car_data = response.json()
        resultat = hämta_bilinformation(car_data, id_lista)
        return resultat

    except requests.RequestException as e:
        print(f"Ett fel uppstod: {e}")
        return None


def hämta_bilinformation(response, id_lista):
    """
    Hämta bilinformation från svaret om det var en framgång.

    :param response: Svaret från call_carinfo(reg_plate).
    :param id_lista: En lista med ID:n som vi vill hämta värden för.

    :return: En ordbok med bilinformation och värden för specifika ID:n, eller ett meddelande om fel.
    """
    # Kolla om svaret är en framgång
    if response.get("success"):
        # Extrahera relevant bilinformation
        result = response.get("result", {})

        bilinfo = {
            "brand": result.get("brand"),
            "series": result.get("series"),
            "model": result.get("model"),
            "generation": result.get("generation"),
            "model_gen_engine": result.get("model_gen_engine"),
            "car_name": result.get("car_name"),
            "chassis": result.get("chassis"),
            "engine": result.get("engine"),
            "engine_type": result.get("engine_type"),
            "horsepower": result.get("horsepower"),
            "engine_start_year": result.get("engine_start_year"),
            "engine_end_year": result.get("engine_end_year"),
            "model_year": result.get("model_year"),
            "trim_package": result.get("trim_package"),
            "licence_plate": result.get("licence_plate"),
            "vin": result.get("vin"),
            "vehicle_type": result.get("vehicle_type"),
            "engine_name": result.get("engine_name"),
            "body_code": result.get("body_code"),
            "sales_name": result.get("sales_name"),
        }

        # Hämta de specifika värdena för varje ID i id_lista
        attributes = result.get("attributes", [])
        resultat = {}

        for id in id_lista:
            for attribut in attributes:
                if attribut.get("id") == str(id):
                    # Lägg till både namn och värden för attributet
                    resultat[id] = {
                        "name": attribut.get("name"),
                        "values": attribut.get("values", []),
                    }
                    break  # Gå vidare till nästa ID

        # Lägg till attributnamn och värden till bilinformationen
        bilinfo["attribute_values"] = resultat
        return bilinfo
    else:
        return {
            "error": "Det gick inte att hämta bilinformation, svar var inte en framgång."
        }


def save_to_json(data, filename, vehicle_types=None):
    """
    Sparar data till en JSON-fil. Hanterar fil som inte finns och ogiltig JSON-data.
    Kollar på 'vehicle_type' och sorterar in fordonet på rätt plats i JSON-strukturen.
    Hanterar svenska tecken (å, ä, ö) korrekt.

    :param vehicle_types: En lista med tillåtna fordonstyper. Om None används en standardlista.
    """
    try:
        # Använd en standardlista om ingen lista anges
        if vehicle_types is None:
            vehicle_types = ["car", "MC"]

        # Läs in befintlig data från JSON-filen
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as file:
                    car_data = json.load(file)
            except json.JSONDecodeError:
                print(f"Ogiltig JSON i {filename}. Skapar ny fil.")
                car_data = {vehicle_type: [] for vehicle_type in vehicle_types}
        else:
            # Om filen inte finns, skapa en ny struktur med tomma listor för varje typ
            car_data = {vehicle_type: [] for vehicle_type in vehicle_types}

        # Kolla på vehicle_type och sortera in i rätt kategori
        vehicle_type = data.get(
            "vehicle_type", ""
        ).lower()  # Hämtar vehicle_type och gör den liten

        # Om den definierade vehicle_type finns i listan, lägg till data i den kategorin
        if vehicle_type in car_data:
            car_data[vehicle_type].append(data)
        else:
            # Om vehicle_type inte finns i listan, lägg till under "others"
            if "others" not in car_data:
                car_data["others"] = []
            car_data["others"].append(data)

        # Spara den uppdaterade datan till fil med UTF-8 kodning
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(car_data, file, indent=4, ensure_ascii=False)
        print(f"Data sparad till {filename}")

    except Exception as e:
        print(f"Fel vid sparning av data till JSON: {e}")
        raise  # Skicka vidare undantaget om du vill hantera det högre upp


reg_plate = "VVV999"
car_info = call_carinfo(reg_plate)
id_lista = [1298, 540]

if car_info:
    print("Fordonets information:", car_info)

    save_to_json(car_info, "car_test.json")

else:
    print("Kunde inte hämta fordonets information.")
