// Lyssna på "keyup"-händelsen i input-fältet för antal mil
document.getElementById('milage-input').addEventListener('keyup', function (event) {
    // Om användaren trycker på Enter-knappen
    if (event.key === 'Enter') {
        console.log("Enter nedtryckt börjar kalkylationer");
        Calc(); // Anropa Calc-funktionen
    }
});

async function Calc() {
    // Hämta värdet från input-fältet
    const inputValue = document.getElementById('milage-input').value;

    // Kontrollera att det är ett positivt heltal och inte tomt
    if (inputValue && !isNaN(inputValue) && inputValue > 0) {
        const milage = parseFloat(inputValue); // Konvertera input till ett tal
        const fuelConsumptionPerMile = 0.6; // Exempel: Bilen förbrukar 0.6 liter per mil
        
        // Beräkna total bensinförbrukning
        const totalFuelConsumed = milage * fuelConsumptionPerMile;
        
        // Visa resultatet i "car-info"-diven
        const carInfoDiv = document.getElementById('car-info');
        carInfoDiv.innerHTML = `
            <p>För ${milage} mil har bilen förbrukat ungefär ${totalFuelConsumed.toFixed(2)} liter bensin.</p>
        `;
    } else {
        alert("Vänligen ange ett giltigt antal mil.");
    }
}
