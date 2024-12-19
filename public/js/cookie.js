document.addEventListener("DOMContentLoaded", () => {
    const banner = document.getElementById("cookie-banner");
    const acceptButton = document.getElementById("accept-cookies");

    // Kontrollera om cookie-inställningen redan finns
    const hasAcceptedCookies = document.cookie
      .split("; ")
      .find((row) => row.startsWith("cookiesAccepted="));

    if (!hasAcceptedCookies) {
      // Visa bannern om cookies inte har accepterats
      banner.classList.remove("hidden");
    }

    acceptButton.addEventListener("click", () => {
      // Sätt en cookie för att indikera att cookies är accepterade
      document.cookie = "cookiesAccepted=true; path=/; max-age=31536000";
      console.log("Accepterade cookies");

      // Dölj bannern
      banner.classList.add("hidden");
    });
  });