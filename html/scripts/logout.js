document.addEventListener("DOMContentLoaded", () => {
  const logoutBtn = document.getElementById("logout");
  if (!logoutBtn) return;

  logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("jwt_token");
    window.location.href = "/login.html";
  });
});