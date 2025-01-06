// Håll reda på aktiva filter
let activeFilters = [];

// Funktion för att hämta JSON-data
async function fetchTiresData() {
  try {
    const response = await fetch('/json/tire_ads.json'); // Ange rätt sökväg till JSON-filen
    const tiresData = await response.json(); // Konvertera till JS-objekt
    initializeTires(tiresData); // Initiera visningen
  } catch (error) {
    console.error('Fel vid hämtning av JSON:', error);
  }
}

// Funktion för att initiera däckvisningen
function initializeTires(tiresData) {
  // Sortera och filtrera direkt vid sidladdning
  sortAndFilterTires(tiresData);

  // Lägg till event listeners på filterknappar
  document.getElementById('All').addEventListener('click', () => toggleFilter('All', tiresData));
  document.getElementById('Summer').addEventListener('click', () => toggleFilter('Summer', tiresData));
  document.getElementById('Winter').addEventListener('click', () => toggleFilter('Winter', tiresData));

  // Lägg till event listener på dropdown-menyn
  document.getElementById('dropdownSort').addEventListener('change', () => sortAndFilterTires(tiresData));
}

// Funktion för att sortera och filtrera däck
function sortAndFilterTires(tiresData) {
  const dropdownValue = document.getElementById('dropdownSort').value;

  let filteredTires = tiresData;

  // Filtrera baserat på aktiva filter
  if (activeFilters.length > 0) {
    filteredTires = filteredTires.filter(tire => activeFilters.includes(tire.Type));
  }

  // Sortera baserat på dropdownvärde
  switch (dropdownValue) {
    case '1': // Rekommenderat (slumpmässig ordning)
      filteredTires = shuffleArray(filteredTires);
      break;
    case '3': // Lägst - Högst
      filteredTires.sort((a, b) => a.Price - b.Price);
      break;
    case '4': // Högst - Lägst
      filteredTires.sort((a, b) => b.Price - a.Price);
      break;
    default:
      // Rekommenderat eller Populär (ingen specifik logik implementerad)
      break;
  }

  updateTiresDisplay(filteredTires);
}

function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1)); // Slumpmässigt index
    [array[i], array[j]] = [array[j], array[i]]; // Byt plats på element
  }
  return array;
}
// Funktion för att uppdatera visningen av däck
function updateTiresDisplay(tires) {
  const container = document.getElementById('tireContainer');
  container.innerHTML = ''; // Rensa befintliga annonser

  tires.forEach(tire => {
    const tireElement = createStyledCard(tire);
    container.appendChild(tireElement);
  });
}

// Funktion för att skapa ett stylat kort
function createStyledCard(tire) {
  // Hämta CSS-variabler från :root
  const rootStyles = getComputedStyle(document.documentElement);
  const containerHeight = rootStyles.getPropertyValue('--containerHeight').trim();
  const containerWidth = rootStyles.getPropertyValue('--containerWidth').trim();
  const imgHeight = rootStyles.getPropertyValue('--imgHeight').trim();
  const infoStart = rootStyles.getPropertyValue('--InfoStart').trim();
  const infoHeight = rootStyles.getPropertyValue('--infoHeigt').trim();
  const titleSize = rootStyles.getPropertyValue('--TitleSize').trim();
  const priceSize = rootStyles.getPropertyValue('--PriceSize').trim();
  const buttonWidth = rootStyles.getPropertyValue('--ButtonWidth').trim();
  const buttonHeight = rootStyles.getPropertyValue('--ButtonHeight').trim();
  const buttonFontSize = rootStyles.getPropertyValue('--ButtonFontSz').trim();
  const buttonPadding = rootStyles.getPropertyValue('--ButtonPadding').trim();
  const graycolor = rootStyles.getPropertyValue('--gra').trim();
  const whiteColor = rootStyles.getPropertyValue('--vit').trim();
  const goldColor = rootStyles.getPropertyValue('--guld').trim();
  const BlackColor = rootStyles.getPropertyValue('--svart').trim();

  // Kortets huvudbehållare
  const card = document.createElement('div');
  card.className = 'container_shopcard';
  card.setAttribute('data-type', tire.Type);
  Object.assign(card.style, {
    backgroundColor: graycolor,
    width: containerWidth,
    height: containerHeight,
    borderRadius: '5%',
    overflow: 'hidden',
    position: 'relative',
    cursor: 'pointer', // Gör att kortet ser klickbart ut
  });

  // Bild
  const img = document.createElement('img');
  img.src = tire.Img;
  img.alt = 'Tire Image';
  img.classList.add('zoom-image');
  Object.assign(img.style, {
    position: 'absolute',
    top: '0',
    left: '0',
    width: '100%',
    height: imgHeight,
    objectFit: 'cover',
  });

  // Info-sektion
  const headInfo = document.createElement('div');
  Object.assign(headInfo.style, {
    position: 'absolute',
    top: infoStart,
    width: '100%',
    height: infoHeight,
    textAlign: 'center',
  });

  // Titel
  const title = document.createElement('h2');
  title.textContent = tire.Title;
  Object.assign(title.style, {
    fontSize: titleSize,
    fontWeight: 'bold',
    color: goldColor,
  });

  // Pris
  const price = document.createElement('div');
  price.textContent = `${tire.Price} :-`;
  Object.assign(price.style, {
    fontSize: priceSize,
    margin: '10px 0',
    fontWeight: 'bold',
  });

  // Köp-knapp (valfritt)
  const button = document.createElement('button');
  button.textContent = 'Köp nu';
  Object.assign(button.style, {
    position: 'absolute',
    bottom: '5%',
    left: '50%',
    transform: 'translateX(-50%)',
    width: buttonWidth,
    height: buttonHeight,
    fontSize: buttonFontSize,
    padding: buttonPadding,
    backgroundColor: BlackColor,
    color: whiteColor,
    borderRadius: '1rem',
    cursor: 'pointer',
  });

  button.addEventListener('click', () => {
    if (tire.Link && tire.Link.startsWith('http')) {
      window.location.href = tire.Link;
    } else {
      alert('Ogiltig länk.');
    }
  });

  // Sätt ihop kortet
  headInfo.appendChild(title);
  headInfo.appendChild(price);
  card.appendChild(img);
  card.appendChild(headInfo);
  card.appendChild(button);

  return card;
}



// Funktion för att hantera filterknappar
function toggleFilter(type, tiresData) {
  const index = activeFilters.indexOf(type);
  if (index > -1) {
    activeFilters.splice(index, 1); // Ta bort filtret om det redan är aktivt
    document.getElementById(type).classList.remove('active'); // Ta bort aktiv klass
  } else {
    activeFilters.push(type); // Lägg till filtret om det inte är aktivt
    document.getElementById(type).classList.add('active'); // Lägg till aktiv klass
  }
  sortAndFilterTires(tiresData); // Uppdatera listan
}

// Hämta och initiera däckvisning vid sidladdning
fetchTiresData();
