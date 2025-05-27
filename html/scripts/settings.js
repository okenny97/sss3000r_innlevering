document.addEventListener('DOMContentLoaded', () => {
  const alarmMode = document.getElementById('alarmMode');
  const emailNotifications = document.getElementById('emailNotifications');
  const appNotifications = document.getElementById('appNotifications');
  const tempInterval = document.getElementById('temp-interval');

  // Hent lagrede innstillinger fra serveren
  fetch('/api/load-settings')
    .then(res => res.json())
    .then(data => {
      if (alarmMode && data.alarmMode) {
        alarmMode.value = data.alarmMode;
      }

      if (emailNotifications && typeof data.emailNotifications !== "undefined") {
        emailNotifications.checked = data.emailNotifications;
      }

      if (appNotifications && typeof data.appNotifications !== "undefined") {
        appNotifications.checked = data.appNotifications;
      }

      if (tempInterval && data.tempUpdateInterval) {
        tempInterval.value = data.tempUpdateInterval;
      }
    })
    .catch(err => console.error("Feil ved henting av innstillinger:", err));

  // Lagrer innstillinger når de endres
  function updateSettings() {
    const settings = {
      alarmMode: alarmMode?.value || "bilde",
      emailNotifications: emailNotifications?.checked || false,
      appNotifications: appNotifications?.checked || false,
      tempUpdateInterval: tempInterval?.value || "60000"
    };

    fetch('/api/save-settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    })
      .then(res => res.json())
      .then(data => console.log("Innstillinger lagret:", data))
      .catch(err => console.error("Feil ved lagring:", err));
  }

  [alarmMode, emailNotifications, appNotifications, tempInterval].forEach(el => {
    if (el) el.addEventListener('change', updateSettings);
  });
});