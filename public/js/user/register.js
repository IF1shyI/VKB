document
    .getElementById("registerForm")
    ?.addEventListener("submit", async (e) => {
      e.preventDefault();

      const name = document.getElementById("name").value;
      const password =document.getElementById("password")
        .value;

      const response = await fetch("http://127.0.0.1:5000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, password }),
      });
      const SucsessDIV = document.getElementById("SucsessDIV");
      const result = await response.json();
      if (result.message === "Användare registrerad och data sparad") {
        SucsessDIV.innerHTML = `
                    <h1>Registrering lyckades! Omdirigeras</h1>
                    `;
        setTimeout(() => {
          window.location.href = "/login"; // Ersätt med URL till inlogging
        }, 1000);
      } else {
        SucsessDIV.innerHTML = `
                    <h1>${result.message}</h1>
                    `;
      }
    });