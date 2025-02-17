import json


def verify_api_key(api_key):
    with open("api_keys.json", "r") as file:
        api_keys = [json.loads(line)["api_key"] for line in file]
    return api_key in api_keys


def search_by_regnumber(regnummer, filename):
    try:
        with open(filename, "r") as file:
            car_data = json.load(file)
        return next(
            (car for car in car_data["bilar"] if car["regnummer"] == regnummer), None
        )
    except FileNotFoundError:
        return None


def save_to_json(data, filename):
    try:
        with open(filename, "r") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {"bilar": []}

    existing_data["bilar"].append(data)

    with open(filename, "w") as file:
        json.dump(existing_data, file, indent=4)
