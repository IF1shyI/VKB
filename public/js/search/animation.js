document.addEventListener("DOMContentLoaded", () => {
  const elements = document.querySelectorAll(".tot-wrapper, .co2-wrapper");

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = 1;
          entry.target.style.transform = "translateY(0)";
          entry.target.style.transition = "opacity 1s ease-out, transform 1s ease-out";
        }
      });
    },
    { threshold: 0.5 }
  );

  elements.forEach((el) => {
    el.style.opacity = 0;
    el.style.transform = "translateY(20px)";
    observer.observe(el);
  });
});
