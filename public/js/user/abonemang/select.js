document.addEventListener("DOMContentLoaded", async () => {
      const loginContainer = document.getElementById("login-container");

      // Försök att hämta användarens tier
      const tier = await getUserTier();

      if (tier) {
        // Lägg till klasser och etikett baserat på användarens tier
        const columns = {
          privat: document.querySelector(".opt1_container"),
          BA: document.querySelector(".opt2_container"),
          pro: document.querySelector(".opt3_container"),
          ftag: document.querySelector(".opt4_container"),
        };

        // Rensa tidigare markeringar och etiketter
        for (const key in columns) {
          columns[key].classList.remove("active", "owned", "recommended");
          const label = columns[key].querySelector(".tier_label");
          if (label) {
            label.remove();
          }

          // Ta bort rekommenderad etikett om användaren äger denna tier
          const recommendedLabel =
            columns[key].querySelector(".recommended_label");
          if (recommendedLabel) {
            recommendedLabel.style.display = "none"; // Ta bort rekommenderad etikett
          }
        }

        // Om användaren äger en tier, markera den som 'owned'
        const activeColumn = columns[tier];

        if (!activeColumn) {
          console.error("Ingen kolumn hittades för tier:", tier);
          return;
        }

        console.log("Aktiv kolumn hittad:", activeColumn);

        // Lägg till klassen för aktiv kolumn och visa "owned"
        activeColumn.classList.add("active", "owned");

        // Lägg till "Äger"-etiketten
        const label = document.createElement("div");
        label.className = "tier_label";
        label.textContent = "Äger";

        const astroCid = activeColumn
          .getAttributeNames()
          .find((attr) => attr.startsWith("data-astro-cid"));
        if (astroCid) {
          label.setAttribute(astroCid, ""); // Applicera samma attribut på den nya "label"
        }
        activeColumn.prepend(label);

        // Ta bort rekommenderat etikett om användaren äger den tiern
        if (tier === "pro") {
          const recommendedColumn = document.querySelector(".opt2_container");
          recommendedColumn.querySelector(".recommended_label").style.display =
            "none"; // Ta bort rekommenderat etikett
        }
      } else {
        // Om token inte är giltig, ta bort den
        console.warn("Token ogiltig, tar bort från localStorage.");
        localStorage.removeItem("jwt");
      }
    });

    // Funktion för att hämta användarens tier
    async function getUserTier() {
      // Hämta JWT från localStorage
      const jwtToken = localStorage.getItem("jwt");

      if (!jwtToken) {
        console.error("JWT-token finns inte i localStorage.");
        return null;
      }

      try {
        // Skicka en begäran till backend för att verifiera JWT och få användarinfo
        const response = await fetch("https://backend.vkbilen.se/checktier", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${jwtToken}`, // Skicka token i Authorization-headern
          },
        });

        // Kontrollera om svaret är OK (status 200)
        if (response.ok) {
          const data = await response.json();
          const tier = data.tier ? data.tier.trim() : null; // Säkerställ att tier finns

          if (tier) {
            return tier;
          } else {
            console.error("Ingen tier-data mottogs från servern.");
            return null;
          }
        } else {
          console.error(
            "Fel vid begäran till servern:",
            response.status,
            response.statusText
          );
          return null;
        }
      } catch (error) {
        console.error("Något gick fel vid hämtning av tier:", error);
        return null;
      }
    }