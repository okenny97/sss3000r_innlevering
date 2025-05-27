const vapidPublicKey = 'BEz_wdm5T0ghim8CCesqZ_PJBDdoF4qsfxjp4PprC0xLBxlmm5s8mk5kbqy2m_q9J1p6tz4AHScqacvFM6x5pkU';

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)));
}

if ('serviceWorker' in navigator && 'PushManager' in window) {
  window.addEventListener('load', async () => {
    try {
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        console.warn('Notifications denied by user');
        return;
      }

      const reg = await navigator.serviceWorker.register('/service-worker.js');
      console.log('Service Worker registered:', reg);

      const subscription = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
      });

      await fetch('/api/subscribe', {
        method: 'POST',
        body: JSON.stringify(subscription),
        headers: { 'Content-Type': 'application/json' }
      });

      console.log('Push subscription successful');
    } catch (err) {
      console.error('Push setup failed:', err);
    }
  });
}