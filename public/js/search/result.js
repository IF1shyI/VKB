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

    const switch_display=document.getElementById("switch_display")

    if (savedCarDataString) {
      let cardata_display = JSON.parse(savedCarDataString);
      console.log("Data: ", cardata_display)
      
      const tier = await getUserTier();
      

      if (cardata_display.fuel_type!="El"){
        const totalFuelCost =
            ((milage * 10) / 100) *
            cardata_display.fuel_consumption *
            cardata_display.fuel_price;
        const tot_pris_real = totalFuelCost + cardata_display.total_cost;
        totpris_display.textContent = tot_pris_real + " KR";
        

        if (tier == "privat" || tier==null) {
        //maintenance
        maintenance_display_service.innerHTML = "<button onclick=\"window.location.href='/abonemang'\">Lås upp</button>";

        tire_cost_display.innerHTML = "<button onclick=\"window.location.href='/abonemang'\">Lås upp</button>";
        
        localStorage.setItem("tot_fuel_cost", totalFuelCost);
        tot_bkostnad.textContent = totalFuelCost + " KR";

        fuel_cost_display.innerHTML = "<button onclick=\"window.location.href='/abonemang'\">Lås upp</button>";


        fuel_consumption_display.innerHTML =
          "<button onclick=\"window.location.href='/abonemang'\">Lås upp</button>";

        //other
        // car_name.textContent = cardata_display.car_name;
        insurance_display.textContent = cardata_display.insurance["liability"]["over_25"] + " KR";

        emission_display.textContent =
          Co2_Emission_calc(milage, cardata_display.Co2_emission) + " KG";
        } else {
          //maintenance
          maintenance_display_service.textContent =
            cardata_display.maintenance_month + " KR";
          tire_cost_display.textContent = cardata_display.tirecost_month + " KR";

          //fuel
          localStorage.setItem("tot_fuel_cost", totalFuelCost);
          tot_bkostnad.textContent = totalFuelCost + " KR";

          fuel_cost_display.textContent = cardata_display.fuel_price + " KR/L";

          fuel_consumption_display.textContent =
            cardata_display.fuel_consumption + " L/100km";

          //other
          insurance_display.textContent = cardata_display.insurance["liability"]["over_25"] + " KR";

          console.log(cardata_display.Co2_emission)
          emission_display.textContent =
            Co2_Emission_calc(milage, cardata_display.Co2_emission) + " KG";
        }
      } else{
        switch_display.textContent = "Kostnad ladda 0-100%"
        
        const tot_pris_real=cardata_display.total_cost + cardata_display.insurance["full"]["over_25"]
        totpris_display.textContent = tot_pris_real + " KR";

        if (tier == "privat" || tier==null){
          fuel_cost_display.innerHTML = "<button onclick=\"window.location.href='/abonemang'\">Lås upp</button>";
          fuel_consumption_display.innerHTML =
          "<button onclick=\"window.location.href='/abonemang'\">Lås upp</button>";
          maintenance_display_service.innerHTML = "<button onclick=\"window.location.href='/abonemang'\">Lås upp</button>";
          tire_cost_display.innerHTML = "<button onclick=\"window.location.href='/abonemang'\">Lås upp</button>";

          insurance_display.textContent = cardata_display.insurance["liability"]["over_25"] + " KR";

        } else{
          const northMiddlePrice = cardata_display.powerprice.find(
            (entry) => entry.north_middle
          )?.north_middle.price;

          const northMiddle0_100 = cardata_display.powerprice.find(
            (entry) => entry.north_middle
          )?.north_middle.cost_battery;

          fuel_cost_display.textContent = northMiddlePrice + " KR/kWh";
          fuel_consumption_display.textContent= northMiddle0_100 + " KR"

          maintenance_display_service.textContent =
            cardata_display.maintenance_month + " KR";
          tire_cost_display.textContent = cardata_display.tirecost_month + " KR";

          insurance_display.textContent = cardata_display.insurance["liability"]["over_25"] + " KR";
        }
      }
      // car_name.textContent = cardata_display.car_name;
      fuel_type_display.textContent = cardata_display.fuel_type;
      emission_display.textContent =
            Co2_Emission_calc(milage, cardata_display.Co2_emission) + " KG";
      maintenance_display.textContent =
          cardata_display.tot_maintenance + " KR";
      skatt_display.textContent = cardata_display.car_tax + " KR";
      } else {
        console.log("No car details found in local storage.");
        window.location.href='/'
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