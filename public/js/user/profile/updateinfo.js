export async function updatedata(data) {
    console.log(data);

    const jwtToken = localStorage.getItem("jwt"); // Hämta JWT från localStorage

    // Kontrollera om token finns innan vi skickar begäran
    if (!jwtToken) {
        console.error("Ingen JWT-token hittades");
        return;
    }

    // Kontrollera att vi har värden för varje parameter, annars sätt undefined
    const firstname = data["first-name"] ? data["first-name"] : undefined;
    const lastname = data["last-name"] ? data["last-name"] : undefined;
    const username = data["username"] ? data["username"] : undefined;
    const email = data.email ? data.email : undefined;
    const success_update = document.getElementById("success_update");

    console.log("hej",data["first-name"], firstname)

    try {
        // Skicka en begäran till backend för att uppdatera profilen
        const response = await fetch("https://backend.vkbilen.se/updateprofile", {
            method: "POST",
            headers: {
                Authorization: `Bearer ${jwtToken}`, // Skicka token i Authorization-headern
                "Content-Type": "application/json", // Viktigt för att skicka JSON
            },
            body: JSON.stringify({
                firstname: firstname, // Skicka undefined om inget värde finns
                lastname: lastname,   // Skicka undefined om inget värde finns
                username: username,   // Skicka undefined om inget värde finns
                email: email          // Skicka undefined om inget värde finns
            }),
        });

        // Hantera svar från servern
        if (response.ok) {
            const result = await response.json();
            success_update.textContent="Dina uppgifter är nu uppdaterade."
        } else {
            console.error("Fel vid uppdatering av profil:", await response.text());
        }
    } catch (error) {
        console.error("Fel vid uppdatering av profil:", error);
    }
}
