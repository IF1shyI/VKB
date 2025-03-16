import { getUserTier } from '../user/usertier.js';

async function Results() {
    const totpris_display = document.getElementById("tot_pris");
    const insurance_display = document.getElementById("insurance_display");
    const tot_bkostnad = document.getElementById("tot_bkostnad");
    const skatt_display = document.getElementById("skatt");
    const maintenance_display = document.getElementById("maintenance_display");
    const maintenance_display_service = document.getElementById(
      "maintenance_display_service"
    );
    const tire_cost_display = document.getElementById(
      "maintenance_display_tire"
    );
    const fuel_cost_display = document.getElementById("bkostnad");
    const fuel_consumption_display = document.getElementById("bbruk_display");
    const fuel_type_display = document.getElementById("dmedeltyp");
    const car_name = document.getElementById("car_name");
    const emission_display = document.getElementById("emission_display");

    const milage = localStorage.getItem("milage");
    const savedCarDataString = localStorage.getItem("cardata");
    const carInfo = JSON.parse(savedCarDataString);

    const switch_display=document.getElementById("switch_display")

    if (carInfo) {
      console.log("Data: ", carInfo)
      

      if (carInfo.fuel_type!="El"){
        const totalFuelCost =Math.round(((milage * 10) / 100) *
            carInfo.fuel_consumption *
            carInfo.fuel_price);
        

        
        //maintenance
        let tot_maintenance = 0;  // För att hålla summan av alla underhållskostnader

        // Iterera genom underhållslistan
        for (let i = 0; i < carInfo.maintenance.length; i++) {
            if (carInfo.maintenance[i].tires) {
                tot_maintenance += carInfo.maintenance[i].tires;  // Lägg till däckkostnaden
            }
            if (carInfo.maintenance[i].service) {
                tot_maintenance += carInfo.maintenance[i].service;  // Lägg till servicekostnaden
            }
        }

        // Visa totala underhållskostnaden
        maintenance_display.textContent = tot_maintenance + " KR";

        // Visa specifik servicekostnad (om det finns)
        maintenance_display_service.textContent = carInfo.maintenance[1].service + " KR";  // Servicekostnaden (index 1)

        // Visa specifik däckkostnad (om det finns)
        tire_cost_display.textContent = carInfo.maintenance[0].tires + " KR";  // Däckkostnaden (index 0)

        const tot_pris_real = Math.round(totalFuelCost + tot_maintenance + carInfo.insurance + carInfo.monthly_tax);
        totpris_display.textContent = tot_pris_real + " KR";
        
        localStorage.setItem("tot_fuel_cost", totalFuelCost);
        tot_bkostnad.textContent = totalFuelCost + " KR";

        fuel_cost_display.textContent = carInfo.fuel_price + " KR/L";


        fuel_consumption_display.textContent = carInfo.fuel_consumption + " l/100km";

        //other
        // car_name.textContent = cardata_display.car_name;
        insurance_display.textContent = carInfo.insurance + " KR";

        skatt_display.textContent = carInfo.monthly_tax + " KR";

        fuel_type_display.textContent = carInfo.fuel_type[0];

        emission_display.textContent =
          Co2_Emission_calc(milage, carInfo.co2_emission) + " KG";
      }
    }

}
  function Co2_Emission_calc(milage, CO2_emission) {
    console.log("miltal och C02 utsläpp: ",milage, CO2_emission)
    const int_milage = parseInt(milage);
    const driving_distance_km = int_milage * 10;
    const total_emisson = (driving_distance_km * CO2_emission) / 1000;
    return total_emisson;
  }

Results();