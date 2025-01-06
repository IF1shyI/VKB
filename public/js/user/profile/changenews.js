export async function changenews() {

    const jwtToken = localStorage.getItem("jwt"); // Hämta JWT från localStorage

    // Kontrollera om token finns innan vi skickar begäran
    if (!jwtToken) {
        console.error("Ingen JWT-token hittades");
        return;
    }

    try {
        // Skicka en begäran till backend för att uppdatera profilen
        const response = await fetch("http://127.0.0.1:5000/togglenews", {
            method: "POST",
            headers: {
                Authorization: `Bearer ${jwtToken}`, // Skicka token i Authorization-headern
                "Content-Type": "application/json", // Viktigt för att skicka JSON
            },
        });

        // Hantera svar från servern
        if (response.ok) {
            const result = await response.json();
            location.reload();
        } else {
            console.error("Fel vid uppdatering av profil:", await response.text());
        }
    } catch (error) {
        console.error("Fel vid uppdatering av profil:", error);
    }
}