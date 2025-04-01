document
    .getElementById("loginForm")
    ?.addEventListener("submit", async (e) => {
      e.preventDefault();

      const usernameInput = document.getElementById("Username");
      const passwordInput = document.getElementById("password");

      const username = usernameInput?.value || "";
      const password = passwordInput?.value || "";

      // Skicka login-request till backend
      const response = await fetch("https://backend.vkbilen.se/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const SucsessDIV = document.getElementById("SucsessDIV");
      const result = await response.json();

      if (response.ok && result.success) {
        // Spara JWT i localStorage
        localStorage.setItem("jwt", result.token);

        SucsessDIV.innerHTML = `
          <h1>${result.message}</h1>
        `;

        setTimeout(() => {
          window.location.href = "/"; // Ersätt med URL till startsidan
        }, 1000);
      } else {
        SucsessDIV.innerHTML = `
          <h1>${result.message}</h1>
        `;
      }
    });