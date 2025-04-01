const reply = await checkadmin();
  if (reply.message == "Autentiserad") {
    document.getElementById("admin_btn").style.display = "block";
  }