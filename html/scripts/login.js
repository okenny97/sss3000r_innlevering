document.addEventListener("DOMContentLoaded", function () {
    console.log("login.js loaded");

    const form = document.getElementById("login-form");
    const twofaSection = document.getElementById("twofa-section");
    const twofaForm = document.getElementById("verifyForm");

    form?.addEventListener("submit", async function (event) {
        event.preventDefault();

        const username = form.username.value;
        const password = form.password.value;

        try {
            const response = await fetch("/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.require_2fa && data.access_token) {
                sessionStorage.setItem("pending_token", data.access_token);

                document.getElementById("login-section").classList.add("d-none");
                twofaSection.classList.remove("d-none");

                if (data.method === "email") {
                    await fetch("/api/send-2fa-code", {
                        method: "POST",
                        headers: {
                            "Authorization": `Bearer ${data.access_token}`
                        }
                    });
                    console.log("📧 Email code sent");
                }

            } else if (data.access_token) {
                localStorage.setItem("jwt_token", data.access_token);
                sessionStorage.removeItem("pending_token");
                window.location.href = "dashboard.html";
            } else {
                alert(data.msg || "Feil brukernavn eller passord");
            }
        } catch (error) {
            console.error("Login request failed:", error);
            alert("Serverfeil. Prøv igjen senere.");
        }
    });

    twofaForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const code = document.getElementById("code").value;
        const token = sessionStorage.getItem("pending_token");

        try {
            const res = await fetch("/api/verify-login-2fa", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ code })
            });

            if (res.ok) {
                localStorage.setItem("jwt_token", token);
                sessionStorage.removeItem("pending_token");
                window.location.href = "dashboard.html";
            } else {
                const data = await res.json();
                document.getElementById("verify-error").textContent = data.msg || "Ugyldig kode";
            }
        } catch (err) {
            console.error("Feil:", err);
            alert("Serverfeil ved verifisering");
        }
    });
    if (!sessionStorage.getItem("pending_token")) {
        twofaSection.classList.add("d-none");
    }
});