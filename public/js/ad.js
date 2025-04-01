  let inactivityTimer;

  const closebtn = document.querySelector(".close-ad");

  function showAd() {
    document.querySelector(".ad-wrapper").classList.add("show");
  }

  function hideAd() {
    document.querySelector(".ad-wrapper").classList.remove("show");
  }

  function resetTimer() {
    clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(showAd, 20000); // Show ad after 20s of inactivity
  }

  // Event listeners for user activity
  document.addEventListener("mousemove", resetTimer);
  document.addEventListener("keydown", resetTimer);
  document.addEventListener("scroll", resetTimer);

  closebtn.addEventListener("click", hideAd)

  // Start the inactivity timer
  resetTimer();