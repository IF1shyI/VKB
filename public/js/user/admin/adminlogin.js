import {checkadmin } from "./admincheck"


const data = await checkadmin();
  if (data.message == "Autentiserad") {
    document.getElementById("admin_cover").classList.add("hide");
  } else {
    window.location.href = "/404"; // Omdirigera till inloggningssidan
  }