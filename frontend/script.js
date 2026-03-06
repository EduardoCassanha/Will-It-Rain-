const API_URL = 'http://127.0.0.1:8000/check-rain';

document.getElementById('btn').addEventListener('click', handleSubmit);

async function handleSubmit() {
    const origin = document.getElementById('origin').value.trim();
    const destination = document.getElementById('destination').value.trim();
    const departure = document.getElementById('departure_time').value.trim();

    if (!origin || !destination) {
        alert('Please fill in origin and destination.');
        return;
    }

    const btn = document.getElementById('btn');
    const result = document.getElementById('result');
    const error = document.getElementById('error');

    btn.disabled = true;
    btn.textContent = 'Checking...';
    result.classList.remove('show');
    error.classList.remove('show');

    try {
        const data = await fetchWeather(origin, destination, departure);

        document.getElementById('verdict').textContent = data.will_rain ? '☂️' : '☀️';
        document.getElementById('recommendation').textContent = data.recommendation;
        document.getElementById('probability').textContent = `Max precipitation probability: ${data.max_precipitation_probability}%`;
        result.classList.add('show');

    } catch (e) {
        error.classList.add('show');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Check';
    }
}

async function fetchWeather(origin, destination, departure) {
    const body = { origin, destination };
    if (departure) body.departure_time = departure.slice(0, 16) + ':00';

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });

    if (!response.ok) throw new Error('API error');

    return await response.json();
}