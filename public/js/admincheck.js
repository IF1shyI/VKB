async function checkadmin() {
    const jwtToken = localStorage.getItem("jwt");
    const admin_cover = document.getElementById("admin_cover");

    // Om det inte finns någon JWT-token, skicka användaren till inloggningssidan
    if (!jwtToken) {
      console.log("Ingen användare är inloggad.");
      window.location.href = "/404"; // Omdirigera till inloggningssidan
      return;
    }
    try {
      // Skicka en begäran till backend för att verifiera JWT och få användarinfo
      const response = await fetch("http://127.0.0.1:5000/admin", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${jwtToken}`, // Skicka token i Authorization-headern
        },
      });

      if (response.ok) {
        const svar_data = await response.json();

        if (svar_data.message != "Autentiserad") {
          window.location.href = "/404"; // Omdirigera till inloggningssidan
          return;
        } else {
          admin_cover.classList.add("hide");
        }
      } else {
        window.location.href = "/404"; // Omdirigera till inloggningssidan
        return;
      }
    } catch (error) {
      console.error("Ett fel uppstod:", error);
    }
  }

  // Kontrollera session direkt vid sidladdning
  checkadmin();