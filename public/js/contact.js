// Client-side JavaScript för att hantera form submission
document.getElementById('contactFormElement').addEventListener('submit', async function (e) {
  e.preventDefault();  // Förhindrar att sidan laddas om

  // Hämta värden från formulärfält
  const name = document.getElementById('name').value;
  const email = document.getElementById('email').value;
  const subject = document.getElementById('subject').value;
  const message = document.getElementById('message').value;

  console.log("Skickar följande data:", { name, email, subject, message });

  try {
    // Skickar POST-förfrågan till API på http://localhost:5000/submit-form
    const response = await fetch('https://backend.vkbilen.se/submit-form', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: name,
        email: email,
        subject: subject,
        message: message,
      }),
    });

    // Kontrollera om svaret är OK (statuskod 200-299)
    if (response.ok) {
      // Dölj formuläret och visa tacksägelsemeddelande om API-svaret är positivt
      document.getElementById('contactFormElement').style.display = 'none';
      const thankYouMessage = document.getElementById('thankYouMessage');
      const contactForm =document.getElementById('contactForm')
      contactForm.classList.add('hide')
      thankYouMessage.style.display = 'block';
      setTimeout(() => {
        thankYouMessage.classList.add('show');
      }, 100);
    } else {
      // Om API:t returnerar ett icke-OK svar (t.ex. 400 eller 500)
      const errorData = await response.json();
      console.error("API fel:", errorData);
      alert('Något gick fel: ' + (errorData.message || 'Försök igen senare.'));
    }
  } catch (error) {
    // Fånga nätverks- eller andra fel och logga dem
    console.error('Fel vid skickandet av formuläret:', error);
    alert('Ett tekniskt fel inträffade. Försök igen senare.');
  }
});
