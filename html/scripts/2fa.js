document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("jwt_token");
  const twofaLabel = document.getElementById("twofa-label");
  const enableBtn = document.getElementById("enable-2fa-btn");
  const disableBtn = document.getElementById("disable-2fa-btn");
  const methodSelect = document.getElementById("methodSelect");
  const methodSection = document.getElementById("twofa-methods");
  const qrArea = document.getElementById("qrArea");

  async function fetchStatus() {
    const res = await fetch("/api/2fa-status", {
      headers: { Authorization: `Bearer ${token}` }
    });
    const data = await res.json();

    if (data.enabled && data.method) {
      twofaLabel.textContent = "Aktivert (" + data.method + ")";
      enableBtn.classList.add("d-none");
      disableBtn.classList.remove("d-none");
    } else {
      twofaLabel.textContent = "Deaktivert";
      enableBtn.classList.remove("d-none");
      disableBtn.classList.add("d-none");
    }
  }

  enableBtn.addEventListener("click", () => {
    methodSection.classList.remove("d-none");
  });

    document.getElementById("save2FA").addEventListener("click", async () => {
        const method = methodSelect.value;

        const res = await fetch("/api/setup-2fa", {
            method: "POST",
            headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ method })
        });

        const data = await res.json();

        if (res.ok) {
            // Skjul dropdown og lagreknappen
            methodSelect.classList.add("d-none");
            document.getElementById("save2FA").classList.add("d-none");

            // Vis QR kode
            if (data.qr_uri) {
            qrArea.innerHTML = `
                <p>Skann QR med Google Authenticator:</p>
                <img src="https://api.qrserver.com/v1/create-qr-code/?data=${encodeURIComponent(data.qr_uri)}&size=200x200">
            `;
            document.getElementById("verifySection").classList.remove("d-none");
            } else {
            qrArea.innerHTML = "<p>Kode sendt til e-post. Skriv den inn under.</p>";
            document.getElementById("verifySection").classList.remove("d-none");
            }
        } else {
            alert("❌ " + (data.msg || "Ukjent feil"));
        }
    });

    document.getElementById("verify2FA").addEventListener("click", async () => {
        const code = document.getElementById("verifyCode").value;
        const res = await fetch("/api/verify-2fa", {
            method: "POST",
            headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
            },
            body: JSON.stringify({ code })
        });

        const data = await res.json();
        const msgEl = document.getElementById("verifyMessage");

        if (res.ok) {
            msgEl.textContent = "✅ 2FA aktivert!";
            msgEl.className = "text-success";
            fetchStatus();
        } else {
            msgEl.textContent = "❌ " + (data.msg || "Ugyldig kode");
            msgEl.className = "text-danger";
        }
    });

    // Skru av 2FA
    disableBtn.addEventListener("click", async () => {
        const res = await fetch("/api/set-2fa", {
            method: "POST",
            headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ method: "none" })
        });

        if (res.ok) {
            alert("❌ 2FA deaktivert");
            methodSection.classList.add("d-none");
            fetchStatus();
            qrArea.innerHTML = "";
        } else {
            alert("Kunne ikke deaktivere 2FA");
        }
    });

  fetchStatus();
});