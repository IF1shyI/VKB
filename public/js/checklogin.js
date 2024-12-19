async function checklogin() {
    const jwtToken = localStorage.getItem("jwt");

    // Om det inte finns någon JWT-token, skicka användaren till inloggningssidan
    if (!jwtToken) {
      console.log("Ingen användare är inloggad.");
      window.location.href = "/login"; // Omdirigera till inloggningssidan
      return;
    }
  }

  // Kontrollera session direkt vid sidladdning
  checklogin();