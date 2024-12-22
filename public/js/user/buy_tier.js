document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".buy_button");
  buttons.forEach((button) => {
    button.addEventListener("click", function () {
      const tier = button.getAttribute("data-tier");
      let tier_name = '';
      let tier_price = '';

      // Hämta tier_name och tier_price baserat på data-tier
      if (tier === 'basanvandare') {
        tier_name = 'Basanvändare';
        tier_price = 50;
      } else if (tier === 'professionell') {
        tier_name = 'Professionell användare';
        tier_price = 200;
      } else if (tier === 'privat') {
        tier_name = 'Privatperson';
        tier_price = 'Gratis';
      } else if (tier === 'ftag') {
        tier_name = 'Företagsanvändare';
        tier_price = 'Anpassat pris';
      }

      // Sätt värdena i localStorage
      localStorage.setItem("tier_name", tier_name);
      localStorage.setItem("tier_price", tier_price);
      localStorage.setItem("buy_tier", tier);

      // Navigera till betalningssidan
      window.location.href = '/payment';
    });
  });
});
