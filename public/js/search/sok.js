import { getUserTier } from '../user/usertier.js';
// Definiera "data" som en global variabel
let data = {}; // Tomt objekt för att hålla bilinformationen

// Lyssna på "keyup"-händelsen istället för "keydown"
document.getElementById('reg-number').addEventListener('keyup', function (event) {
    const inputValue = event.target.value;

    // Kontrollera om längden är exakt 6 tecken och om användaren tryckte på Enter
    if (inputValue.length === 6 && event.key === 'Enter') {
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

async function Search() {
    

    localStorage.removeItem('cardata')
    // Hämta värdet från input-fältet
    const inputValue = document.getElementById('reg-number').value;
    const carInfoDiv = document.getElementById('car-info');
    const loadingMessage = document.getElementById('loading-message');
    const bensinbrukval = document.getElementById('bbruk-display')

    // Kontrollera om längden är exakt 6 tecken
    if (inputValue.length === 6) {
        // Visa laddningsmeddelande
        loadingMessage.style.display = 'block';
        carInfoDiv.innerHTML = '';  // Töm tidigare resultat
        

            try {
                const jwtToken=localStorage.getItem('jwt')
                const user_tier=await getUserTier()
                const response = await fetch("http://localhost:5000/can_search?user_tier=" + user_tier, {
                method: "GET",
                headers: {
                    Authorization: `Bearer ${jwtToken}`,
                }
                });

                const ok_search_data = await response.json();
                if (ok_search_data.can_search) {
                console.log("Användaren kan söka!");
                try {
                    // Skicka en HTTP GET-begäran till Flask-API:t
                    const response = await fetch(`http://127.0.0.1:4000/carcost?reg_plate=${inputValue}&key=testperson-1734630806.015074`, {
                        method: "GET", // GET används eftersom Flask-routen förväntar sig det
                    });
                    
                    // Logga svaret för felsökning

                    if (!response.ok) {
                        throw new Error(`Network response was not ok: ${response.statusText}`);
                    }

                    // Tilldela global variabel "data" med API-svaret
                    data = await response.json();
                    if (data.error) {
                        console.log("API svarade med: ", data.error);
                        carInfoDiv.innerHTML = `
                                <p>${data.car_name ? data.car_name : 'Problem uppstod. Försök igen senare'}</p>
                                `;
                    // Visa meddelande till användaren
                    } else {
                    // API-svaret innehåller bilinformationen
                        console.log(data)
                        localStorage.setItem('cardata', JSON.stringify(data));
                        console.log('Car data saved to localStorage:', data);
                        // Visa informationen på sidan
                        carInfoDiv.innerHTML = `
                            <p>${data.car_name ? data.car_name : 'Hittar inte bilmodell. Försök igen senare'}</p>
                            `;
                    }
                } catch (error) {
                    // Hantera fel och visa ett meddelande
                    carInfoDiv.innerHTML = `<p>Fel: ${error.message}</p>`;
                    console.error("Fel vid hämtning av data:", error);
                } finally {
                    // Dölj laddningsmeddelandet
                    loadingMessage.style.display = 'none';
                }
                if (data.message != "Try again later"){
                    toggleStep();
                }
                } else {
                console.log(`Kan inte söka: ${data.message}`);
                const loading_message=document.getElementById('loading-message')
                const error_info=document.getElementById('car-info')
                error_info.textContent="Slut på sökningar, testa igen senare."
                loading_message.classList.add('hidden')
                }
            } catch (error) {
                console.error("Error:", error);
            }
        

        
        
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
    if (inputValue && !isNaN(inputValue) && inputValue > 0) {
        const milage_num = parseFloat(inputValue); // Konvertera input till ett tal
        localStorage.setItem('milage', milage_num)
        window.location.href='/resultat'
    }
}
