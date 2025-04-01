document.addEventListener("DOMContentLoaded", function () {
    const dropdownWrapper = document.querySelector(".dropdown-wrapper");
    const dropdownItems = document.querySelector(".dropdown-items");
    const dropdownIcon = document.querySelector(".dropdown-content img");
    const resultContainer = document.querySelector(".result-container");
    const svgIcon = document.querySelector(".tilde svg");

    // Kontrollera att svgIcon verkligen finns innan vi försöker ändra dess stil
    if (!svgIcon) {
        console.error("SVG icon not found!");
        return; // Avbryt om SVG:n inte finns
    }

    // Lägg till transition och transform-origin för SVG om den finns
    svgIcon.style.transition = "transform 0.3s ease-in-out";
    svgIcon.style.transformOrigin = "center";  // För att rotera runt mitten

    dropdownWrapper.addEventListener("click", function (event) {
        event.stopPropagation();
        const isOpen = dropdownItems.classList.contains("open");

        if (!isOpen) {
            dropdownItems.classList.add("open");
            dropdownWrapper.style.borderBottomRightRadius = "0";
            dropdownWrapper.style.borderBottomLeftRadius = "0";

            resultContainer.style.transition = "margin-bottom 0.3s ease-in-out";
            resultContainer.style.marginBottom = "0";

            setTimeout(function () {
                const height = dropdownItems.scrollHeight;
                dropdownItems.style.transition = "height 0.4s ease-in-out, opacity 0.3s";
                dropdownItems.style.height = `${height}px`;
                dropdownItems.style.opacity = "1";
                resultContainer.style.marginBottom = `${height}px`;
            }, 10);
        } else {
            dropdownItems.style.height = "0";
            dropdownItems.style.opacity = "0";
            dropdownWrapper.style.borderBottomRightRadius = "5px";
            dropdownWrapper.style.borderBottomLeftRadius = "5px";
            resultContainer.style.marginBottom = "0";

            setTimeout(() => dropdownItems.classList.remove("open"), 400);
        }

        // Rotation för ikonen
        svgIcon.style.transform = isOpen ? "rotate(0deg)" : "rotate(180deg)";
        svgIcon.style.transition = "transform 0.3s ease-in-out";

        // Rotation för SVG
        if (svgIcon) {
            svgIcon.style.transform = isOpen ? "rotate(0deg)" : "rotate(180deg)";
            svgIcon.style.transition = "transform 0.3s ease-in-out";
        }
    });

    document.addEventListener("click", function (event) {
        if (!dropdownWrapper.contains(event.target)) {
            dropdownItems.style.height = "0";
            dropdownItems.style.opacity = "0";
            resultContainer.style.marginBottom = "0";
            dropdownIcon.style.transform = "rotate(0deg)";
            
            if (svgIcon) {
                svgIcon.style.transform = "rotate(0deg)";
            }

            setTimeout(() => dropdownItems.classList.remove("open"), 400);
        }
    });
});
