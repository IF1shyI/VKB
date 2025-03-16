from app.utils.helpers import extract_value_by_label


def extract_car_info(tree):
    """Extrahera relevant information från HTML-dokumentet med lxml och XPath"""
    car_info = {}

    try:
        # Hitta alla <div class="info">-element
        info_divs = tree.xpath('//div[@class="info"]')

        # Gå igenom varje <div class="info"> och kontrollera innehållet
        for div in info_divs:
            # Extrahera text från <em> och <span>
            em_text = div.xpath(".//em/text()")
            span_text = div.xpath(".//span/text()")

            # Kontrollera om bränsletyp finns i texten
            if em_text and span_text:
                if "Förbrukning" in span_text[0]:
                    if em_text[0] == "Okänd" and car_info["type"] == "Personbil":
                        consumption = 6
                    elif em_text[0] == "Okänd" and car_info["type"] == "Motorcykel":
                        consumption = 4
                    else:
                        consumption = float(em_text[0].replace(" l/100km", "").strip())
                    car_info["fuel_consumption"] = consumption

                if "Typ" in span_text[0]:
                    car_info["type"] = em_text[0]

                if "Utsläpp" in span_text[0]:
                    if em_text[0] == "-":
                        co2_value = 0
                    else:
                        co2_value = float(em_text[0].replace(" g/km", "").strip())

                    car_info["co2_emission"] = co2_value

                if "Bränsle" in span_text[0]:
                    cleaned_fuel_types = (
                        em_text[0].strip().replace("\n", "").split(", ")
                    )
                    car_info["fuel_type"] = cleaned_fuel_types

                if "Modellår" in span_text[0]:
                    car_info["year"] = em_text[0]

                if "Växellåda" in span_text[0]:
                    car_info["transmission"] = em_text[0]

                if "Drivhjul" in span_text[0]:
                    car_info["drive_wheels"] = em_text[0]

                if "Hästkrafter" in span_text[0]:
                    Horsepwr = float(em_text[0].replace(" HK", "").strip())
                    car_info["horsepower"] = Horsepwr
    except Exception as e:
        print(f"[ERROR] Kan inte extrahera relevant data: {e}")

    annual_tax = extract_value_by_label(tree, "Årlig skatt")
    car_info["monthly_tax"] = round(
        float(annual_tax.replace(" SEK", "").strip()) / 12, 2
    )

    make = extract_value_by_label(tree, "Fabrikat")
    car_info["make"] = make

    model = extract_value_by_label(tree, "Modell")
    car_info["model"] = model

    return car_info
