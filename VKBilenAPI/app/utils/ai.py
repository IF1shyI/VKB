from openai import OpenAI
from dotenv import load_dotenv
import os
import re

load_dotenv()

AIKEY = os.getenv("CHATGPT_KEY")

client = OpenAI(
    # This is the default and can be omitted
    api_key=AIKEY,
)


def contact_ai(promt):

    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": promt,
            }
        ],
        model="gpt-4o-mini",
    )
    return response


async def get_maintenance(data):

    try:
        maintenance_prompt = f"""
            Please provide only the annual costs for a {data["make"]} {data["model"]} in the following categories in Swedish kronor (SEK), formatted exactly as shown below:

            maintenance: [Enter amount]
            Tire replacement cost: [Enter amount]
            other repairs: [Enter amount]

            Provide only the numbers for each category without any delimiters (e.g., commas or spaces), and DO NOT include a total or summary.

            """

        response = contact_ai(maintenance_prompt)

        # Hämta svaret från AI-modellen
        maintenancecost = response.choices[0].message.content

        # Om ingen data returnerades
        if not maintenancecost.strip():
            print("Ingen data mottogs från AI.")
            return None

        # Förbered för att extrahera data med hjälp av regex
        nested_list = []

        # Dela upp svaret rad för rad
        for line in maintenancecost.strip().split("\n"):
            if ":" in line:
                title, amount = line.split(":", 1)
                try:
                    # Försök omvandla beloppet till ett heltal
                    amount_clean = amount.strip().replace(" ", "")
                    nested_list.append(
                        [
                            title.strip().replace(" ", ""),
                            round(int(amount_clean) / 12),
                            2,
                        ]
                    )
                except ValueError as e:
                    # Om omvandlingen misslyckas, skriv ut felmeddelande
                    print(
                        f"Fel vid omvandling av belopp på raden: '{line}'. Error: {e}"
                    )
                    continue

            # Kontrollera om data extraherades korrekt
            if not nested_list:
                print("Ingen giltig data extraherades. Försök igen.")
                return None

            data["maintenance"] = nested_list

    except Exception as e:
        # Fångar oväntade fel och skriver ut dem för felsökning
        print(f"Ett oväntat fel inträffade: {e}")
        return None


async def get_insurance(data):
    try:
        insurance_prompt = f"""
        I want you to act as an insurance agent or company. Based on the following details of the car, provide a reasonable estimate of the annual cost for a comprehensive car insurance (fully comprehensive insurance) in Swedish kronor (SEK).

        Here are the car details:

        - Make: {data["make"]}
        - Model: {data["model"]}
        - Year: {data["year"]}
        - Fuel Type: {', '.join(data["fuel_type"])}
        - Horsepower: {data["horsepower"]} HK
        - Monthly Tax: {data["monthly_tax"]} SEK

        Please provide only the estimated annual cost in SEK as a number, with no additional explanation, details, or factors included. Just the number, in SEK.
        """

        # Skicka förfrågan till AI-modellen
        response = contact_ai(insurance_prompt)

        # Hämta råsvaret från AI:n
        raw_prices = response.choices[0].message.content.strip()
        data["insurance"] = round(float(raw_prices) / 12, 2)

    except Exception as e:
        # Fångar oväntade fel och skriver ut dem för felsökning
        print(f"Ett oväntat fel inträffade: {e}")
        return None
