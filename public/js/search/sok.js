import { getUserTier } from '../user/usertier.js';
// Definiera "data" som en global variabel
let data = {}; // Tomt objekt för att hålla bilinformationen

const btn = document.getElementById("search-car");
btn.addEventListener('click', () =>{
    const inputValue = document.getElementById('reg-number').value;

    if (btn.classList.contains('calc')){
        Calc();
        exit
    }

    // Kontrollera om längden är exakt 6 tecken och om användaren tryckte på Enter
    if (inputValue.length === 6) {
        hidebtn();
        Search(); // Anropa din Search-funktion

    }
})

// Lyssna på "keyup"-händelsen istället för "keydown"
document.getElementById('reg-number').addEventListener('keyup', function (event) {
    const inputValue = event.target.value;

    // Kontrollera om längden är exakt 6 tecken och om användaren tryckte på Enter
    if (inputValue.length === 6 && event.key === 'Enter') {
        hidebtn();
        Search(); // Anropa din Search-funktion
    }
});

// Lyssna på "keyup"-händelsen i input-fältet för antal mil
document.getElementById('milage-input').addEventListener('keyup', function (event) {
    // Om användaren trycker på Enter-knappen
    if (event.key === 'Enter') {
        Calc(); // Anropa Calc-funktionen
    }
});

let mskatt = 0;
let totMaintenance;

function hidebtn(){
    btn.classList.add('calc')
    btn.style.display = "none"
    btn.textContent = "Räkna ut"
}

async function Do_search(inputValue) {
    const carInfoDiv = document.getElementById('car-info');
    const loadingMessage = document.getElementById('loading-message');
    loadingMessage.style.display = 'block';  // Visa laddningsmeddelandet

    try {
        // Skicka GET-begäran till Flask-API:t
        const carResponse = await fetch(`https://api.vkbilen.se/car/cost?reg_plate=${inputValue}`, {
            method: "GET",
            credentials: "include"
        });

        if (!carResponse.ok) {
            console.error("API call failed:", carResponse.status, await carResponse.text());
            throw new Error(`Network response was not ok: ${carResponse.statusText}`);
        }

        // Tilldela data till variabeln "carData"
        const carData = await carResponse.json();

        if (carData.error) {
            console.log("API svarade med: ", carData.error);
            carInfoDiv.innerHTML = `
                <p>${carData.car_name ? carData.car_name : 'Problem uppstod. Försök igen senare'}</p>
            `;
        } else {
            // API-svaret innehåller bilinformation
            console.log(carData);
            data = getCarInfo(carData)
            localStorage.setItem('cardata', JSON.stringify(data));
            console.log('Car data saved to localStorage:', data);
            carInfoDiv.innerText = data.name;
        }

        // Kontrollera om användaren ska kunna fortsätta
        if (carData.message !== "Try again later") {
            toggleStep();
        } else {
            console.log(`Kan inte söka: ${carData.message}`);
            carInfoDiv.innerHTML = "Slut på sökningar, testa igen senare.";
        }
    } catch (error) {
        // Felhantering om något går fel
        console.error("Fel vid hämtning av data:", error);
        carInfoDiv.innerHTML = `<p>Fel: ${error.message}</p>`;
    } finally {
        // Dölj laddningsmeddelandet när allt är klart
        loadingMessage.style.display = 'none';
    }
}


async function Search() {
    // Ta bort tidigare bilinformation från localStorage
    localStorage.removeItem('cardata');
    
    // Hämta värdet från input-fältet
    const inputValue = document.getElementById('reg-number').value;
    const carInfoDiv = document.getElementById('car-info');
    const loadingMessage = document.getElementById('loading-message');
    
    // Kontrollera om längden är exakt 6 tecken
    if (inputValue.length === 6) {
        // Visa laddningsmeddelande
        loadingMessage.style.display = 'block';
        carInfoDiv.innerHTML = '';  // Töm tidigare resultat

        try {
            const jwtToken = localStorage.getItem('jwt');

            if (!jwtToken) {
                // Hämta användarens IP-adress om det inte finns något JWT
                const response = await fetch('https://api.ipify.org?format=json');
                const data = await response.json();
                console.log('Din IP-adress är:', data.ip);

                await Do_search(inputValue);
                btn.style.display = "block"

        
            } else {

                await Do_search(inputValue);
                btn.style.display = "block"
            }
        } catch (error) {
            console.error("Fel vid hämtning av data:", error);
            carInfoDiv.innerHTML = `<p>Fel vid hämtning av data: ${error.message}</p>`;
        } finally {
            // Dölj laddningsmeddelandet
            loadingMessage.style.display = 'none';
        }
    } else {
        carInfoDiv.innerHTML = '<p>Registreringsnumret måste vara exakt 6 tecken långt.</p>';
        loadingMessage.style.display = 'none';
    }
}


function toggleStep() {
    console.log("Försöker toggla klass på elementet .step-two");
    const stepTwoElement = document.querySelector('.step-two');
    const reginput = document.querySelector(".reg-input-wrapper");
    
    if (stepTwoElement) {
        stepTwoElement.classList.toggle('hidden');
        reginput.classList.toggle('hidden');
    } else {
        console.error("Element med klassen 'step-two' hittades inte");
    }
}

let bensinkostnad = 0;
async function Calc() {
    // Hämta värdet från input-fältet
    const inputValue = document.getElementById('milage-input').value;
    if (inputValue && !isNaN(inputValue) && inputValue > 0) {
        const milage_num = parseFloat(inputValue); // Konvertera input till ett tal
        localStorage.setItem('milage', milage_num)
        window.location.href='/resultat'
    }
}

function getCarInfo(carData) {
    let carInfo;

    // Check if carData.data is an array or an object
    if (Array.isArray(carData.data)) {
        // If it's an array, access the first element
        carInfo = carData.data[0].car_info;
    } else if (carData.data && carData.data.car_info) {
        // If it's an object, access car_info directly
        carInfo = carData.data.car_info;
    } else {
        // Handle the case when car_info is not found
        console.error("Car info is not available in the expected format.");
    }

    return carInfo;
}