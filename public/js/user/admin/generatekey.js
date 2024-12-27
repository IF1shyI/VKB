async function handleGenerateKey(userName, userEmail) {
    const key_display = document.getElementById("key_display");

    if (!userName || !userEmail) {
      console.error("Användarnamn och e-postadress krävs");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:4000/create_api_key", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_name: userName, user_mail: userEmail }),
      });

      if (!response.ok) {
        throw new Error("Misslyckades med att skapa API-nyckel: " + response.statusText);
      }

      const data = await response.json();
      console.log("API-nyckel skapad:", data.raw_key);
      key_display.textContent = "Din API-nyckel: " + data.raw_key;
    } catch (error) {
      console.error("Ett fel uppstod:", error);
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const usernameField = document.getElementById("new_api_user_username");
    const emailField = document.getElementById("new_api_user_email");
    const button = document.getElementById("submit_btn");
    const key_display = document.getElementById("key_display");

    if (usernameField && emailField && button) {
      // Kollar om elementen finns
      button.addEventListener("click", function () {
        const userName = usernameField.value;
        const userEmail = emailField.value;
        console.log("Knappen trycktes. Användarnamn:", userName, "E-postadress:", userEmail);
        handleGenerateKey(userName, userEmail);
      });

      usernameField.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          const userName = usernameField.value;
          const userEmail = emailField.value;
          e.preventDefault();
          console.log("Enter trycktes. Användarnamn:", userName, "E-postadress:", userEmail);
          handleGenerateKey(userName, userEmail);
        }
      });

      emailField.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          const userName = usernameField.value;
          const userEmail = emailField.value;
          e.preventDefault();
          console.log("Enter trycktes. Användarnamn:", userName, "E-postadress:", userEmail);
          handleGenerateKey(userName, userEmail);
        }
      });
    } else {
      console.log("Elementen finns inte i DOM.");
    }
});
