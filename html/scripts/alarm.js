document.addEventListener("DOMContentLoaded", () => {
    const toggleAlarm = document.getElementById("toggle-alarm");
    const alarmStatusWord = document.getElementById("alarm-status-word");

    let alarmOn = false;

    function updateAlarmUI() {
        if (alarmOn) {
            alarmStatusWord.innerText = "på";
            alarmStatusWord.classList.remove("text-danger");
            alarmStatusWord.classList.add("text-success");
            toggleAlarm.textContent = "Slå av alarm";
            toggleAlarm.classList.remove("btn-success");
            toggleAlarm.classList.add("btn-danger");
        } else {
            alarmStatusWord.innerText = "av";
            alarmStatusWord.classList.remove("text-success");
            alarmStatusWord.classList.add("text-danger");
            toggleAlarm.textContent = "Slå på alarm";
            toggleAlarm.classList.remove("btn-danger");
            toggleAlarm.classList.add("btn-success");
        }
    }

    toggleAlarm.addEventListener("click", async () => {
        if (!alarmOn) {
            // Alarm på
            try {
                const res = await fetch('/api/run-pir', { method: 'POST' });
                const data = await res.json();
                console.log("✅ Alarm started:", data);

                if (res.ok) {
                    alarmOn = true;
                    updateAlarmUI();
                    alert("🔔 Alarmen er nå på!");
                } else {
                    alert(data.error || "Kunne ikke starte alarmen.");
                }
            } catch (err) {
                console.error("❌ Error starting alarm:", err);
                alert("Kunne ikke starte alarmen.");
            }
        } else {
            // Alarm av
            try {
                const res = await fetch('/api/stop-pir', { method: 'POST' });
                const data = await res.json();
                console.log("✅ Alarm stopped:", data);

                if (res.ok) {
                    alarmOn = false;
                    updateAlarmUI();
                    alert("🔕 Alarmen er nå av!");
                } else {
                    alert(data.error || "Kunne ikke stoppe alarmen.");
                }
            } catch (err) {
                console.error("❌ Error stopping alarm:", err);
                alert("Kunne ikke stoppe alarmen.");
            }
        }
    });

    // Sjekk status på alarmen når siden lastes inn
    fetch('/api/status-pir')
    .then(res => res.json())
    .then(data => {
        alarmOn = (data.status === "running");
        updateAlarmUI();
        console.log("ℹ️ Alarm status on load:", data.status);
    })
    .catch(err => {
        console.error("❌ Error checking alarm status:", err);
    });
});