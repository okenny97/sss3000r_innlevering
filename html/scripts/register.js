document.addEventListener("DOMContentLoaded", () => {
  const registerForm = document.getElementById("registerForm");
  const msgBox = document.getElementById("register-message");

  // Last inn brukere
  loadUsers();

  if (!registerForm) return;

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const form = e.target;
    const username = form.username.value;
    const email = form.email.value;
    const password = form.password.value;

    try {
      const token = localStorage.getItem("jwt_token");

      const res = await fetch("/api/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ username, email, password })
      });

      let data;
      try {
        data = await res.json();
      } catch (err) {
        const text = await res.text();
        console.error("Response is not JSON:", text);
        alert("Serverfeil: " + text);
        return;
      }

      if (res.ok) {
        msgBox.textContent = "Bruker registrert!";
        msgBox.className = "alert alert-success mt-3";
        msgBox.classList.remove("d-none");
        form.reset();
        loadUsers();
      } else {
        msgBox.textContent = (data.msg || "Ukjent feil");
        msgBox.className = "alert alert-danger mt-3";
        msgBox.classList.remove("d-none");
      }

    } catch (err) {
      console.error("Serverfeil:", err);
      alert("Serverfeil. Prøv igjen senere.");
    }
  });
});

async function loadUsers() {
  const token = localStorage.getItem("jwt_token");
  if (!token) return;

  try {
    const res = await fetch("/api/users", {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    const data = await res.json();
    const tbody = document.getElementById("user-table-body");
    tbody.innerHTML = "";

    data.forEach(user => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${user.username}</td>
        <td>${user.email}</td>
      `;
      tbody.appendChild(row);
    });

  } catch (err) {
    console.error("Klarte ikke hente brukerliste:", err);
  }
}