document.addEventListener("DOMContentLoaded", function () {
    const dropdownWrapper = document.querySelector(".dropdown-wrapper");
    const dropdownItems = document.querySelector(".dropdown-items");
    const dropdownIcon = document.querySelector(".dropdown-content img");
    const resultContainer = document.querySelector(".result-container");

    dropdownWrapper.addEventListener("click", function (event) {
        event.stopPropagation(); // Förhindra att klick utanför direkt stänger den
        
        const isOpen = dropdownItems.classList.contains("open");
        
        if (!isOpen) {
            dropdownItems.classList.add("open");
            dropdownWrapper.style.borderBottomRightRadius = "0";
            dropdownWrapper.style.borderBottomLeftRadius = "0";

            // Sätt transition för margin-bottom i resultContainer via JavaScript
            resultContainer.style.transition = "margin-bottom 0.3s ease-in-out"; // Detta görs via JavaScript nu

            // Börja med att sätta en liten margin på resultContainer så att den "faller ner" i takt med dropdownen
            resultContainer.style.marginBottom = "0";  // Börja med 0 margin

            // Lägg till en timeout för att vänta på att dropdownen är öppen
            setTimeout(function () {
                const height = dropdownItems.getBoundingClientRect().height;
                dropdownItems.style.transition = "height 0.4s ease-in-out";
                dropdownItems.style.height = `${height}px`; // Sätt höjden på dropdownen dynamiskt

                // Samtidigt, sätt marginBottom på resultContainer till samma höjd som dropdown
                resultContainer.style.marginBottom = `${height}px`;
            }, 10); // Vänta lite för att dropdownen ska börja röra sig innan höjden sätts
        } else {
            dropdownItems.classList.remove("open");
            dropdownWrapper.style.borderBottomRightRadius = "5px";
            dropdownWrapper.style.borderBottomLeftRadius = "5px";
            resultContainer.style.marginBottom = "0"; // Återställ margin när dropdown är stängd
        }

        dropdownIcon.style.transform = isOpen ? "rotate(0deg)" : "rotate(180deg)";
        dropdownIcon.style.transition = "transform 0.3s ease-in-out";
    });

    document.addEventListener("click", function (event) {
        if (!dropdownWrapper.contains(event.target)) {
            dropdownItems.classList.remove("open");
            dropdownIcon.style.transform = "rotate(0deg)";
            resultContainer.style.marginBottom = "0"; // Återställ margin när dropdown stängs
        }
    });
});
