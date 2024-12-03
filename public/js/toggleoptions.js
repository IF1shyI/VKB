// Vänta på att sidan ska laddas innan eventlyssnare läggs till
document.addEventListener("DOMContentLoaded", function() {
  // Hämta knappen
  const toggleButton = document.getElementById("toggleButton");
  // Lägg till eventlyssnare
  toggleButton.addEventListener("click", toggleOptions);
});

// Funktion för att toggla klasser
function toggleOptions(event) {
  event.stopPropagation(); // Stoppa bubbling av click-eventet
  const options = document.querySelector(".options"); // Hämta .options-elementet
  const valdiv = document.getElementById("ValID");

  // Använd toggle() för att lägga till/ta bort klasser
  options.classList.toggle("hidden");
  options.classList.toggle("show");
  valdiv.classList.toggle("val_toggled");

}
