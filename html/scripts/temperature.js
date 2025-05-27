let intervalId;

function fetchTemperature() {
  fetch('/api/temperature')
    .then(response => response.json())
    .then(data => {
      const display = document.getElementById('temperature-display');
      if (data.temperature) {
        display.textContent = `Temperature: ${data.temperature} °C`;
      } else {
        display.textContent = 'Temperature: Error';
      }
    })
    .catch(error => {
      console.error('Error fetching temperature:', error);
      document.getElementById('temperature-display').textContent = 'Temperature: Error';
    });
}

function startTemperatureUpdates(interval) {
  clearInterval(intervalId);
  fetchTemperature();
  intervalId = setInterval(fetchTemperature, interval);
}

document.addEventListener('DOMContentLoaded', () => {
  const defaultInterval = 60000;
  const savedInterval = parseInt(localStorage.getItem('tempUpdateInterval')) || defaultInterval;
  startTemperatureUpdates(savedInterval);
});