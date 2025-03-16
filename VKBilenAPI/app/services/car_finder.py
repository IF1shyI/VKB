from app.models import db, Car
from app.utils.fetch_car_data import fetch_data
from app.utils.ai import get_insurance
from app.utils.calc_maintenance import calc_maintenance
from app.utils.helpers import today_fuelprice, save_to_json
import asyncio
import aiohttp


async def get_car_info(reg_plate):
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(fetch_data(session, reg_plate))
        car_info = results[0]["car_info"]
        car_info["reg"] = reg_plate
        await asyncio.gather(
            get_insurance(car_info),
            calc_maintenance(car_info),
        )
        save_to_json(car_info, "vehicles.json")
        await today_fuelprice(car_info)
        print("\n==== SAMMANFATTNING ====\n")
        for res in results:
            print(res)
        return results
