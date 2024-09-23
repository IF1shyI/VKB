// Definiera "data" som en global variabel
let data = {}; // Tomt objekt för att hålla bilinformationen

// Lyssna på "keyup"-händelsen istället för "keydown"
document.getElementById('reg-number').addEventListener('keyup', function (event) {
    const inputValue = event.target.value;

    // Kontrollera om längden är exakt 6 tecken och om användaren tryckte på Enter
    if (inputValue.length === 6 && event.key === 'Enter') {
        console.log("Enter nedtryckt och 6 tecken uppnått");
        Search(); // Anropa din Search-funktion
    }
});

// Lyssna på "keyup"-händelsen i input-fältet för antal mil
document.getElementById('milage-input').addEventListener('keyup', function (event) {
    // Om användaren trycker på Enter-knappen
    if (event.key === 'Enter') {
        console.log("Enter nedtryckt börjar kalkylationer");
        Calc(); // Anropa Calc-funktionen
    }
});

let mskatt = 0;

async function Search() {
    // Hämta värdet från input-fältet
    const inputValue = document.getElementById('reg-number').value;
    const carInfoDiv = document.getElementById('car-info');
    const loadingMessage = document.getElementById('loading-message');

    console.log("Sökning startad för registreringsnummer:", inputValue);

    // Kontrollera om längden är exakt 6 tecken
    if (inputValue.length === 6) {
        // Visa laddningsmeddelande
        loadingMessage.style.display = 'block';
        carInfoDiv.innerHTML = '';  // Töm tidigare resultat

        try {
            // Skicka en HTTP GET-begäran till Flask-API:t
            const response = await fetch(`http://127.0.0.1:5000/bilinfo?reg_plate=${inputValue}`);
            
            // Logga svaret för felsökning
            console.log("Respons från API:", response);

            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }

            // Tilldela global variabel "data" med API-svaret
            data = await response.json();

            // Logga data för felsökning
            console.log("Data från API:", data);
            
            // Visa informationen på sidan
            carInfoDiv.innerHTML = `
                <p>${data.car_model ? data.car_model : 'Hittar inte bilmodell'}</p>
                `;
            

            const skatt = document.getElementById('skatt');

            console.log("Skatt", data.fskatt)
            if (data.fskatt !== 0){
                mskatt = data.fskatt / 12;
            }
            skatt.innerHTML = `
                <p>${mskatt.toFixed(2)}</p>
            `;
            console.log("Data hämtad och visad");
        } catch (error) {
            // Hantera fel och visa ett meddelande
            carInfoDiv.innerHTML = `<p>Fel: ${error.message}</p>`;
            console.error("Fel vid hämtning av data:", error);
        } finally {
            // Dölj laddningsmeddelandet
            loadingMessage.style.display = 'none';
        }

        // Toggla steg eller nästa del av sidan
        toggleStep();
    } else {
        carInfoDiv.innerHTML = '<p>Registreringsnumret måste vara exakt 6 tecken långt.</p>';
        loadingMessage.style.display = 'none';
    }
}


function toggleStep() {
    console.log("Försöker toggla klass på elementet .step-two");
    const stepTwoElement = document.querySelector('.step-two');
    
    if (stepTwoElement) {
        stepTwoElement.classList.toggle('show');
        console.log("Klass togglades på .step-two");
    } else {
        console.error("Element med klassen 'step-two' hittades inte");
    }
    console.log("Försöker toggla klass på elementet .input-wrapper");
    const stepTwo = document.querySelector('.input-wrapper');
    
    if (stepTwo) {
        stepTwo.classList.toggle('hide');
        console.log("Klass togglades på .input-wrapper");
    } else {
        console.error("Element med klassen 'input-wrapper' hittades inte");
    }
    console.log("Försöker toggla klass på elementet .reg-num-label");

    const stepTwolable = document.querySelector('.reg-num-label');
    
    if (stepTwolable) {
        stepTwolable.classList.toggle('hide');
        console.log("Klass togglades på .reg-num-label");
    } else {
        console.error("Element med klassen '.reg-num-label' hittades inte");
    }
}

let bensinkostnad = 0;
async function Calc() {
    // Hämta värdet från input-fältet
    const inputValue = document.getElementById('milage-input').value;
    const loadingMessage = document.getElementById('loading-message');

    // Kontrollera att det är ett positivt heltal och inte tomt
    if (inputValue && !isNaN(inputValue) && inputValue > 0) {
        const milage = parseFloat(inputValue); // Konvertera input till ett tal

        loadingMessage.style.display = 'block';

        // Hämta bränslepriser från Flask API
        const prices = await getFuelPrices();

        const insurance_cost =  await getInsurance();
        
        console.log("Försäkringskostnad ",insurance_cost)
        // Hämtar och stripar till drivmedel (Diesel/Bensin)
        const drivmedel = (data.drivmedel || '')
        .split(/[\|,]/)[0]  // Dela upp med både "|" och ","
        .trim();  // Ta bort extra mellanslag
        
        // Logga data.besbruk för att se vad som faktiskt finns där
        console.log("Bensinförbrukning (data.besbruk):", data.besbruk);

        // Använd bilens förbrukning eller ett standardvärde om det saknas
        const fuelConsumptionPerMile = (data.besbruk && !isNaN(data.besbruk)) ? parseFloat(data.besbruk) : 0.5;

        // Kontrollera att fuelConsumptionPerMile är ett giltigt tal
        console.log("Korrekt bensinförbrukning:", fuelConsumptionPerMile);

        // Beräkna total bensinförbrukning
        const totalFuelConsumed = milage * fuelConsumptionPerMile;

        // Deklarera variabler för pris och kostnad
        let bpris = 0;
        const drivmedelPris = document.getElementById('bkostnad')
        const drivmedeltyp = document.getElementById('dmedeltyp')


        // Kontrollera drivmedel och hämta rätt pris
        if (drivmedel === "Bensin") {
            console.log("Drivmedel är Bensin");
            bpris = prices.petrolPrice; // Använd direkt som numeriskt värde
            bensinkostnad = totalFuelConsumed * bpris;
            drivmedelPris.innerHTML = `
            <p>${bpris.toFixed(2)} kr/l</p>
            `;
            drivmedeltyp.innerHTML = `
            <div>Kostnad ${drivmedel}</div>
            `;
        } else if (drivmedel === "Diesel") {
            console.log("Drivmedel är Diesel");
            bpris = prices.dieselPrice; // Använd direkt som numeriskt värde
            bensinkostnad = totalFuelConsumed * bpris;
            drivmedelPris.innerHTML = `
            <p>${bpris.toFixed(2)} kr/l</p>
            `;
            drivmedeltyp.innerHTML = `
            <div>Kostnad ${drivmedel}</div>
            `;
        } else {
            console.log("Okänt drivmedel");
            alert("Drivmedlet är okänt.");
            return; // Avsluta funktionen om drivmedlet är okänt
        }

        // Visa resultatet i "car-info"-diven
        // const carInfoDiv = document.getElementById('car-info');
        // carInfoDiv.innerHTML = `
        //     <p>För ${milage} mil har bilen förbrukat ungefär ${totalFuelConsumed.toFixed(2)} liter ${drivmedel}.</p>
        //     <p>Aktuellt ${drivmedel}pris: ${bpris.toFixed(2)} kr per liter</p>
        //     <p>Kostnad för ${drivmedel}: ${bkostnad.toFixed(2)} kr</p>
        // `;

        const Bensinkostnad = document.getElementById('tot-bkostnad');
        Bensinkostnad.innerHTML = `
            <p>${bensinkostnad.toFixed(2)}</p>
        `;

        loadingMessage.style.display = 'none'

        Results()
    } else {
        alert("Vänligen ange ett giltigt antal mil.");
    }
}





async function getFuelPrices() {
    try {
        const response = await fetch('http://127.0.0.1:5000/fuel-prices');
        if (!response.ok) {
            throw new Error('Något gick fel vid hämtning av bränslepriser');
        }
        const prices = await response.json();
        console.log('Bensinpris:', prices.petrolPrice);
        console.log('Dieselpris:', prices.dieselPrice);
        return prices;
    } catch (error) {
        console.error('Fel:', error);
    }
}

let insuranceNumber

let insuranceCost = 0;  // Definiera en global variabel för att spara försäkringskostnaden

async function getInsurance() {
    try {
        const response = await fetch('http://127.0.0.1:5000/insurance');
        if (!response.ok) {
            throw new Error('Något gick fel vid hämtning av försäkringskostnader');
        }

        const insuranceData = await response.json();
        // Se till att försäkringskostnaden kommer in som nummer
        insuranceCost = Number(insuranceData.average_price_month);  // Spara försäkringskostnaden globalt

        if (isNaN(insuranceCost)) {
            throw new Error('Försäkringskostnaden är inte ett giltigt nummer');
        }

        // Visa försäkringskostnaden i UI
        const insuranceCostMonth = document.getElementById('insurance_display');
        insuranceCostMonth.innerHTML = `<p>${insuranceCost.toFixed(2)}</p>`;
        
    } catch (error) {
        console.error('Fel:', error);
    }
}

async function Results() {
    const totpris = document.getElementById('tot-pris');

    // Kontrollera att värdena är numeriska
    const bkostnadNum = Number(bensinkostnad);
    const fskattNum = Number(data.fskatt / 12);

    if (isNaN(bkostnadNum) || isNaN(fskattNum) || isNaN(insuranceCost)) {
        console.error('Felaktiga värden: Kontrollera bensinkostnad, fordonsskatt eller försäkringskostnad');
        return;
    }

    // Summera värdena
    const totsum = bkostnadNum + fskattNum + insuranceCost;

    // Format med två decimaler och tusenavgränsare
    const formattedSum = totsum.toLocaleString('sv-SE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    // Sätt in resultatet i elementet "totpris"
    totpris.innerHTML = `
        ${formattedSum} KR
    `;

    console.log("Försöker visa resultat");
    const resultatElement = document.querySelector('.result-container');
    
    if (resultatElement) {
        resultatElement.classList.toggle('show');
        console.log("Klass togglades på .result-container");
    } else {
        console.error("Element med klassen 'result-container' hittades inte");
    }
}
