async function handleGenerateKey(userName) {
    const key_display = document.getElementById("key_display");
    if (!userName) {
      console.error("Användarnamn krävs");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:4000/create_api_key", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ user_name: userName }),
      });

      if (!response.ok) {
        throw new Error("Failed to create API key: " + response.statusText);
      }

      const data = await response.json();
      console.log("API-nyckel skapad:", data.raw_key);
      key_display.textContent = "Din API-nykel: " + data.raw_key;
    } catch (error) {
      console.error("Ett fel uppstod:", error);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    const inputField = document.getElementById("new_api_user_username");
    const button = document.getElementById("submit_btn");

    if (inputField && button) {
      // Check if elements exist
      button.addEventListener("click", function () {
        const username = inputField.value;
        console.log("Knappen trycktes. Användarnamn:", username);
        handleGenerateKey(username);
      });

      inputField.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          const username = inputField.value;
          e.preventDefault();
          console.log("Enter trycktes. Användarnamn:", username);
          handleGenerateKey(username);
        }
      });
    } else {
      console.log("Elementen finns inte i DOM.");
    }
  });