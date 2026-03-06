const API_URL = 'http://127.0.0.1:8000/check-rain';

document.getElementById('btn').addEventListener('click', handleSubmit);

function handleSubmit() {
    const origin = document.getElementById('origin').value.trim();
    const destination = document.getElementById('destination').value.trim();
    const departure = document.getElementById('departure_time').value.trim();

    if (!origin || !destination) {
        alert('Please fill in origin and destination.');
        return;
    }

    console.log({ origin, destination, departure });
}

async function fetchWeather(origin, destination, departure) {
    const body = { origin, destination };
    if (departure) body.departure_time = departure.slice(0, 16) + ':00';

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    })

    if (!response.ok) throw new Error('API error');

    return await response.json();
}