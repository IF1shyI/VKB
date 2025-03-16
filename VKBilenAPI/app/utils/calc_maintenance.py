# Definiera dina parametrar

# Distans körd år (km)
avrage_distance = 1126 * 10  # 11260 km per år

# Kostnad service (kr)
service_cost_petrol = 2500
service_cost_diesel = 4000
service_cost_natural_gas = 6000
service_cost_el = 3000

# Service intervall (km)
service_interval_petrol = 12000
service_interval_diesel = 15000
service_interval_natural_gas = 10000
service_interval_el = 25000

# Däck hållbarhet (km)
tire_life_distance = 40000  # Däckens livslängd är 40 000 km, inte 40 000 * 10

# Kostnader däckbyte
tire_changing_cost = 5000  # Kostnaden för byte av däck
tire_cost = 600 * 4  # Kostnaden för 4 nya däck


async def calc_maintenance(data):
    nested_list = []

    # Beräkna årlig däckkostnad
    tires_yearly = avrage_distance / tire_life_distance
    tires_change_cost = tires_yearly * (
        tire_cost + tire_changing_cost
    )  # Totala däckkostnaden per år
    nested_list.append({"tires": round(tires_change_cost / 12)})

    # Beräkna årlig servicekostnad baserat på bränsletyp
    if data["fuel_type"][0] == "Bensin":
        services_yearly = avrage_distance / service_interval_petrol
        service_price = service_cost_petrol * services_yearly
        nested_list.append({"service": round(service_price / 12)})

    elif data["fuel_type"][0] == "Diesel":
        services_yearly = avrage_distance / service_interval_diesel
        service_price = service_cost_diesel * services_yearly
        nested_list.append({"service": round(service_price / 12)})

    elif data["fuel_type"][0] == "El":
        services_yearly = avrage_distance / service_interval_el
        service_price = service_cost_el * services_yearly
        nested_list.append({"service": round(service_price / 12)})

    data["maintenance"] = nested_list
