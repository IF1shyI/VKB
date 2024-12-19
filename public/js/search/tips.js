const cardata = localStorage.getItem('cardata');
const milage = localStorage.getItem('milage')
const tot_fuel_cost=localStorage.getItem('tot_fuel_cost')
const total_emisson=localStorage.getItem('total_emisson')
console.log(tot_fuel_cost)
    if (cardata) {
        let cardata_display = JSON.parse(cardata);
        console.log('Retrieved car details:', cardata_display);

        const high_fuel = cardata_display.fuel_consumption * 0.8
        const low_fuel = cardata_display.fuel_consumption * 0.7

        const high_cost =high_fuel * milage * cardata_display.fuel_price
        const low_cost =low_fuel * milage*cardata_display.fuel_price
        console.log(high_cost, low_cost)

        // const totprisH = totfbrukH * cardata_display.fuel_price
        // const totprisL = totfbrukL * cardata_display.fuel_price

        const SparH = tot_fuel_cost - high_cost
        const SparL = tot_fuel_cost - low_cost

        const Tspar = (SparH + SparL)/2

        const Co2sH = total_emisson*0.3
        const Co2sL = total_emisson*0.2

        const Co2tot = (Co2sH + Co2sL)/2

        console.log('Har kört js för att hitta diff', SparH, SparL, Tspar)
        const SparandeH = document.getElementById('SparH');
        SparandeH.innerHTML = `${SparH.toFixed(0)}`;

        const SparandeL = document.getElementById('SparL');
        SparandeL.innerHTML = `${SparL.toFixed(0)}`;

        const Totaltspar = document.getElementById('TotSpar')
        Totaltspar.innerHTML = `${Tspar.toFixed(0)}`;

        const Co2sparL =document.getElementById('co2sparL')
        Co2sparL.innerHTML = `${Co2sL.toFixed(0)}`;

        const Co2sparH =document.getElementById('co2sparH')
        Co2sparH.innerHTML = `${Co2sH.toFixed(0)}`;

        const C02Tot =document.getElementById('C02Tot')
        C02Tot.innerHTML = `${Co2tot.toFixed(0)}`;
    }