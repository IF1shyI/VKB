document.querySelector(".send-back-btn").addEventListener("click", function() {
            window.scrollTo({
                top: 0,  // Scrolla till toppen av sidan
                left: 0,  // Ingen horisontell scroll
                behavior: "smooth"  // Smooth scroll (det gör scrollen mjuk)
            });
        });