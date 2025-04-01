async function Update_tier(new_tier) {
    if (!new_tier) {
        console.error("Ingen ny plan vald.");
        return;
    }

    const jwtToken = localStorage.getItem("jwt");  // Hämta JWT-token från localStorage
    if (!jwtToken) {
        console.error("Ingen JWT-token tillgänglig.");
        return;
    }

    try {
        const response = await fetch("https://backend.vkbilen.se/update_tier", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${jwtToken}`,  // Använd JWT-token för autentisering
            },
            body: JSON.stringify({ new_tier }),  // Skicka new_tier i body som JSON
        });

        const result = await response.json();

        if (result && result.success) {  // Om servern svarar med en lyckad uppdatering
            console.log("Plan uppdaterad!");
            localStorage.removeItem("buy_tier");  // Ta bort den gamla planen från localStorage
            // Du kan lägga till en meddelande till användaren om lyckad uppdatering
        } else {
            console.error("Uppdatering misslyckades:", result.message || "Ingen information");
        }
    } catch (error) {
        console.error("Fel vid uppdatering:", error);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const new_tier = localStorage.getItem("buy_tier");  // Hämta den nya planen från localStorage
    if (new_tier) {
        Update_tier(new_tier);  // Uppdatera planen om det finns en ny
    } else {
        console.log("Ingen ny plan vald.");
    }
});
