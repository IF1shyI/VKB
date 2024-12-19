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

    if (savedCarDataString) {
      let cardata_display = JSON.parse(savedCarDataString);
      
      const tier = await getUserTier();
      
      if (tier == "privat" || tier==null) {
        //maintenance
        maintenance_display.textContent =
          cardata_display.tot_maintenance + " KR";
        maintenance_display_service.innerHTML = "<button onclick=\"window.location.href='/abonemang'\">Lås upp</button>";

        tire_cost_display.innerHTML = "<button onclick=\"window.location.href='/abonemang'\">Lås upp</button>";

        //fuel
        const totalFuelCost = Math.round(
          ((milage*10) / 100) *
          cardata_display.fuel_consumption *
          cardata_display.fuel_price
        );
        
        localStorage.setItem("tot_fuel_cost", totalFuelCost);
        tot_bkostnad.textContent = totalFuelCost + " KR";

        fuel_cost_display.innerHTML = "<button onclick=\"window.location.href='/abonemang'\">Lås upp</button>";

        fuel_type_display.textContent = cardata_display.fuel_type;

        fuel_consumption_display.innerHTML =
          "<button onclick=\"window.location.href='/abonemang'\">Lås upp</button>";

        //other
        car_name.textContent = cardata_display.car_name;
        insurance_display.textContent = cardata_display.insurance + " KR";
        skatt_display.textContent = cardata_display.car_tax + " KR";

        const tot_pris_real = totalFuelCost + cardata_display.total_cost;
        totpris_display.textContent = tot_pris_real + " KR";
        emission_display.textContent =
          Co2_Emission(milage, cardata_display.fuel_type) + " KG";
      } else {
        //maintenance
        maintenance_display.textContent =
          cardata_display.tot_maintenance + " KR";
        maintenance_display_service.textContent =
          cardata_display.maintenance_month + " KR";
        tire_cost_display.textContent = cardata_display.tirecost_month + " KR";

        //fuel
        const totalFuelCost =
          ((milage * 10) / 100) *
          cardata_display.fuel_consumption *
          cardata_display.fuel_price;
        console.log(totalFuelCost);
        localStorage.setItem("tot_fuel_cost", totalFuelCost);
        tot_bkostnad.textContent = totalFuelCost + " KR";

        fuel_cost_display.textContent = cardata_display.fuel_price + " KR/L";
        fuel_type_display.textContent = cardata_display.fuel_type;

        fuel_consumption_display.textContent =
          cardata_display.fuel_consumption + " L/100km";

        //other
        car_name.textContent = cardata_display.car_name;
        skatt_display.textContent = cardata_display.car_tax + " KR";
        insurance_display.textContent = cardata_display.insurance + " KR";

        const tot_pris_real = totalFuelCost + cardata_display.total_cost;
        totpris_display.textContent = tot_pris_real + " KR";

        emission_display.textContent =
          Co2_Emission(milage, cardata_display.fuel_type) + " KG";
      }
    } else {
      console.log("No car details found in local storage.");
    }
  }

  function Co2_Emission(milage, drivmedel) {
    const int_milage = parseInt(milage);
    const driving_distance_km = int_milage * 10;

    
    if (drivmedel == "Diesel") {
      const Co2_bruk = 120;
      const total_emisson = (driving_distance_km * Co2_bruk) / 1000;
      return total_emisson;
    }
    if (drivmedel == "Bensin") {
      const Co2_bruk = 140;
      const total_emisson = (driving_distance_km * Co2_bruk) / 1000;
      return total_emisson;
    }
  }

Results();