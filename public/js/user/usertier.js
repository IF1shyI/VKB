export async function getUserTier() {
  // Hämta JWT från localStorage
  const jwtToken = localStorage.getItem("jwt");

  if (!jwtToken) {
    console.error("JWT-token finns inte i localStorage.");
    return null;
  }

  try {
    // Skicka en begäran till backend för att verifiera JWT och få användarinfo
    const response = await fetch("https://backend.vkbilen.se/checktier", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${jwtToken}`, // Skicka token i Authorization-headern
      },
    });

    // Kontrollera om svaret är OK (status 200)
    if (response.ok) {
      const data = await response.json();
      const tier = data.tier ? data.tier.trim() : null;  // Säkerställ att tier finns

      if (tier) {
        return tier;
      } else {
        console.error("Ingen tier-data mottogs från servern.");
        return null;
      }
    } else {
      console.error("Fel vid begäran till servern:", response.status, response.statusText);
      return null;
    }
  } catch (error) {
    console.error("Något gick fel vid hämtning av tier:", error);
    return null;
  }
}