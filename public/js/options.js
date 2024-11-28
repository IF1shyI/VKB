// Håll reda på de aktiva filtren
let activeFilters = [];

function sortTires() {
  const dropdownValue = document.getElementById('dropdownSort').value;

  let sortedTires;

  switch (dropdownValue) {
    case '1':
      // Rekommenderat, ingen specifik sortering
      sortedTires = tiresData; // Här kan du lägga till logik för att sortera baserat på rekommenderat om du har sådan data
      break;

    case '2':
      // Populär (Antar att du har någon popularitetsordning, t.ex. rankad lista)
      sortedTires = tiresData; // Om du har populära däcken ordnade, implementera det här
      break;

    case '3':
      // Lägst - Högst
      sortedTires = [...tiresData].sort((a, b) => a.Price - b.Price);
      break;

    case '4':
      // Högst - Lägst
      sortedTires = [...tiresData].sort((a, b) => b.Price - a.Price);
      break;

    default:
      sortedTires = tiresData;
  }

  updateTiresDisplay(sortedTires); // Uppdatera däcken med den sorterade listan
  
}

// Funktion för att uppdatera visningen av däcken
function updateTiresDisplay() {
  const cards = document.querySelectorAll('.container'); // Alla däckkort
  cards.forEach(card => {
    const type = card.getAttribute('data-type'); // Hämta däcktyp från kortet
    // Visa eller dölj kortet beroende på om det matchar det aktiva filtret
    if (activeFilters.length === 0 || activeFilters.includes(type)) {
      card.style.display = 'block'; // Visa kortet
    } else {
      card.style.display = 'none'; // Dölj kortet
    }
  });
}

// Funktion för att hantera knapptryckningar
function toggleFilter(type) {
  const index = activeFilters.indexOf(type);
  if (index > -1) {
    activeFilters.splice(index, 1); // Ta bort filtret om det redan är aktivt
    document.getElementById(type).classList.remove('active'); // Ta bort aktiv klass
  } else {
    activeFilters.push(type); // Lägg till filtret om det inte är aktivt
    document.getElementById(type).classList.add('active'); // Lägg till aktiv klass
  }
  updateTiresDisplay(); // Uppdatera däcken
}

// Lägg till event listeners på knapparna
document.getElementById('All').addEventListener('click', () => toggleFilter('All'));
document.getElementById('Summer').addEventListener('click', () => toggleFilter('Summer'));
document.getElementById('Winter').addEventListener('click', () => toggleFilter('Winter'));

// Initial uppdatering av däcken när sidan laddas
updateTiresDisplay();

