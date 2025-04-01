document.addEventListener("DOMContentLoaded", async () => {
    const jwtToken = localStorage.getItem("jwt");

    const logout_button = document.getElementById("logout_button");

    logout_button.addEventListener("click", async () => {
      // Här används rätt variabelnamn
      try {
        // Skicka en begäran till backend för att verifiera JWT och logga ut
        const response = await fetch("https://backend.vkbilen.se/logout", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${jwtToken}`, // Skicka token i Authorization-headern
          },
        });

        if (response.ok) {
          const data = await response.json();
          if (data.message) {
            localStorage.removeItem("jwt");
            console.log(data.message);
            window.location.href = "/"; // Omdirigera till startsidan
          }
        } else {
          console.error("Servern returnerade ett fel:", response.status);
        }
      } catch (error) {
        console.error("Fel vid utloggning:", error);
      }
    });
  });

export async function logout() {
  const jwtToken = localStorage.getItem("jwt");
  try {
        // Skicka en begäran till backend för att verifiera JWT och logga ut
        const response = await fetch("https://backend.vkbilen.se/logout", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${jwtToken}`, // Skicka token i Authorization-headern
          },
        });

        if (response.ok) {
          const data = await response.json();
          if (data.message) {
            localStorage.removeItem("jwt");
            console.log(data.message);
            window.location.href = "/"; // Omdirigera till startsidan
          }
        } else {
          console.error("Servern returnerade ett fel:", response.status);
        }
      } catch (error) {
        console.error("Fel vid utloggning:", error);
      }
}