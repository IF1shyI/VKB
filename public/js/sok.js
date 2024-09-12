async function Search() {
            // Hämta värdet från input-fältet
            const inputValue = document.getElementById('reg-number').value;
            const carInfoDiv = document.getElementById('car-info');
            const loadingMessage = document.getElementById('loading-message');

            // Kontrollera om längden är exakt 6 tecken
            if (inputValue.length === 6) {
                // Visa laddningsmeddelande
                loadingMessage.style.display = 'block';
                carInfoDiv.innerHTML = '';

                try {
                    // Skicka en HTTP GET-begäran till Flask-API:t
                    const response = await fetch(`http://127.0.0.1:5000/bilinfo?reg_plate=${inputValue}`);
                    
                    if (!response.ok) throw new Error('Network response was not ok');
                    
                    const data = await response.json();
                    
                    // Visa informationen på sidan
                    carInfoDiv.innerHTML = `
                        <p>Registreringsnummer: ${data.reg_plate}</p>
                        <p>Bilmodell: ${data.car_model}</p>
                        <p>Bensinförbrukning: ${data.besbruk}</p>
                        <p>Fordonsskatt: ${data.fskatt}</p>
                    `;
                } catch (error) {
                    // Hantera fel och visa ett meddelande
                    carInfoDiv.innerHTML = `<p>Fel: ${error.message}</p>`;
                } finally {
                    // Dölj laddningsmeddelandet
                    loadingMessage.style.display = 'none';
                }
            } else {
                carInfoDiv.innerHTML = '<p>Registreringsnumret måste vara exakt 6 tecken långt.</p>';
                loadingMessage.style.display = 'none';
            }
        }