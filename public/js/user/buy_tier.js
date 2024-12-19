async function buyTier(tier) {
  const jwtToken = localStorage.getItem('jwt');

  if (!jwtToken) {
    alert("Du måste vara inloggad för att uppgradera din plan.");
    return;
  }

  // Skicka en begäran till backend för att initiera betalningen
  try {
    const response = await fetch('http://127.0.0.1:5000/initiate_payment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${jwtToken}`
      },
      body: JSON.stringify({ tier: tier }) // Skicka vilket tier användaren vill köpa
    });

    const data = await response.json();

    if (data.client_secret) {
      // Om betalningen initierades framgångsrikt, omdirigera användaren till betalningssidan
      localStorage.setItem("client_secret", data.client_secret);
      localStorage.setItem("tier_name", tier);
      localStorage.setItem("tier_price", data.amount / 100); // Omräknat till SEK

      // Omdirigera användaren till /payment där de kan skriva in e-post och slutföra betalningen
      window.location.href = '/payment';
    } else {
      alert("Fel vid betalning. Försök igen senare.");
    }
  } catch (error) {
    console.error("Fel vid betalning:", error);
    alert("Ett problem uppstod vid betalningen.");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".buy_button");
  buttons.forEach((button) => {
    button.addEventListener("click", function () {
      const tier = button.getAttribute("data-tier");
      buyTier(tier);
    });
  });
});
