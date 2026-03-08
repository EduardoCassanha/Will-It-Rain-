const i18n = {
    en: {
        subtitle: "Check if you need an umbrella for your trip",
        originLabel: "Origin",
        destinationLabel: "Destination",
        departureLabel: "Departure",
        originPlaceholder: "e.g. Campinas, São Paulo",
        destinationPlaceholder: "e.g. Guarulhos, São Paulo",
        btn: "Check",
        btnLoading: "Checking...",
        alertFields: "Please fill in origin and destination.",
        noRecommendation: "No recommendation available.",
        umbrella: "Take an umbrella!",
        good: "You're good to go!",
        maxProb: (prob) => `Max precipitation probability: ${prob}%`,
        around: (hour) => ` around ${hour}:00h`,
    },
    pt: {
        subtitle: "Veja se você precisa de guarda-chuva na sua viagem",
        originLabel: "Origem",
        destinationLabel: "Destino",
        departureLabel: "Horário de saída (opcional)",
        originPlaceholder: "ex: Barueri, São Paulo",
        destinationPlaceholder: "ex: Mackenzie, São Paulo",
        btn: "Verificar",
        btnLoading: "Verificando...",
        alertFields: "Preencha origem e destino.",
        alertPast: "O horário de saída não pode estar no passado.",
        noRecommendation: "Nenhuma recomendação disponível.",
        umbrella: "Leve um guarda-chuva!",
        good: "Pode ir tranquilo!",
        maxProb: (prob) => `Probabilidade máxima de chuva: ${prob}%`,
        around: (hour) => ` por volta das ${hour}h.`,
    }
}

let currentLang = localStorage.getItem('lang') || 'en';

const API_URL = 'https://api.will-it-rain.cassanha.com/check-rain';

document.getElementById('btn').addEventListener('click', handleSubmit);

async function handleSubmit() {
    const origin = document.getElementById('origin').value.trim();
    const destination = document.getElementById('destination').value.trim();
    const departure = document.getElementById('departure_time').value.trim();

    if (!origin || !destination) {
        alert('Please fill in origin and destination.');
        return;
    }

    if (departure) {
        const selectedTime = new Date(departure);
        const now = new Date();
        now.setSeconds(0, 0);

        if (selectedTime < now) {
            alert('Departure time cannot be in the past.');
            return;
        }
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
        document.getElementById('recommendation').textContent = data.recommendation || "No recommendation available.";

        const prob = data.max_precipitation_probability ?? 0;

        let detailText = `Max precipitation probability: ${prob}%`;

        if (data.route_weather && data.route_weather.length > 0) {
            const maxPoint = data.route_weather.reduce((prev, current) =>
                (prev.precipitation_probability > current.precipitation_probability) ? prev : current
            );

            if (maxPoint.precipitation_probability > 0) {
                const hour = new Date(maxPoint.time).getHours();
                detailText += ` around ${hour}:00h.`;
            }
        }

        document.getElementById('probability').textContent = detailText;
        result.classList.add('show');

    } catch (e) {
        const errorElement = document.getElementById('error');
        errorElement.textContent = e.message;
        errorElement.classList.add('show');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Check';
    }
}

async function fetchWeather(origin, destination, departure) {
    const body = { origin, destination };
    if (departure) body.departure_time = departure;

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || 'API error';
        throw new Error(errorMessage);
    }

    return await response.json();
}