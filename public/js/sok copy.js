// Lyssna på "keyup"-händelsen istället för "keydown"
document.getElementById('reg-number').addEventListener('keyup', function (event) {
    const inputValue = event.target.value;

    // Kontrollera om längden är exakt 6 tecken och om användaren tryckte på Enter
    if (inputValue.length === 6 && event.key === 'Enter') {
        console.log("Enter nedtryckt och 6 tecken uppnått");
        Search(); // Anropa din Search-funktion
    }
});

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

            const data = await response.json();

            // Logga data för felsökning
            console.log("Data från API:", data);
            
            // Visa informationen på sidan
            carInfoDiv.innerHTML = `
                <p>Registreringsnummer: ${data.reg_plate}</p>
                <p>Bilmodell: ${data.car_model}</p>
                <p>Bensinförbrukning: ${data.besbruk ? data.besbruk : 'Information saknas'}</p>
                <p>Fordonsskatt: ${data.fskatt ? data.fskatt + ' SEK' : 'Information saknas'}</p>`
                ;

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
