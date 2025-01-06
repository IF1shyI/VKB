export async function getinfo() {
    const jwtToken = localStorage.getItem("jwt"); // Hämta JWT från localStorage


    
    // Kontrollera om token finns innan vi skickar begäran
    if (!jwtToken) {
        console.error("Ingen JWT-token hittades");
        return;
    }
    
    try {
      // Skicka en begäran till backend för att logga ut
        const response = await fetch("http://127.0.0.1:5000/profileinfo", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${jwtToken}`, // Skicka token i Authorization-headern
        },
        });

        if (response.ok) {
        const data = await response.json();
        console.log(data)
        return data
        } else {
        console.error("Fel vid utloggning:", await response.text());
        }
    } catch (error) {
        console.error("Fel vid utloggning:", error);
    }
}
