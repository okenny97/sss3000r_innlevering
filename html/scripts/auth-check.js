function isTokenExpired(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    const now = Math.floor(Date.now() / 1000);
    return payload.exp && payload.exp < now;
  } catch {
    return true;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("jwt_token");
  const currentPath = window.location.pathname;

  const isLoginPage = currentPath.endsWith("/login.html") || currentPath === "/login.html";

  console.log("auth-check.js → current path:", currentPath);
  console.log("isLoginPage?", isLoginPage);
  console.log("JWT token:", token);

  if (!token || isTokenExpired(token)) {
    localStorage.removeItem("jwt_token");

    if (!isLoginPage) {
      window.location.href = "/login.html";
    } else {
      document.body.style.display = "block";
    }
  } else {
    if (isLoginPage) {
      window.location.href = "/dashboard.html";
    } else {
      document.body.style.display = "block";
    }
  }
});