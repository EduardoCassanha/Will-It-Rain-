# Will It Rain? 🌧️

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)
![Status](https://img.shields.io/badge/Status-Functional-brightgreen?style=flat)

> **Don't just check the weather at your destination. Check it along the way.**

A REST API with a web interface that tells you whether it will rain **during your journey**, not just at your destination. Given an origin, destination, and departure time, it maps your route, estimates when you'll reach each point, and checks the forecast at the right time for each location.

![API Response](assets/will_it_rain.png)

**Live:** [will-it-rain.cassanha.com](https://will-it-rain.cassanha.com)

---

## The Problem

Most weather apps check a single location at a single time. But if you're driving 2 hours across the city, rain at your destination in 30 minutes doesn't mean you'll get wet, and clear skies now doesn't mean you'll stay dry. **Will It Rain?** solves this by treating your route as a timeline, not a single point.

---

## How It Works
```
Origin + Destination + Departure Time
          ↓
  Geocoding (LocationIQ)
  Converts addresses → coordinates
          ↓
  Routing (OpenRouteService)
  Calculates full route + total duration
          ↓
  Route Segmentation
  Splits route into dynamic points based on distance
  Estimates arrival time at each point
          ↓
  Weather Forecast (Open-Meteo)
  Queries precipitation at each point
  at the correct estimated time
          ↓
  Result: max precipitation probability
  + recommendation
```

---

## Features

- **Route-aware forecasting** — checks weather at each point along the route, not just origin or destination
- **Time-accurate predictions** — estimates when you'll actually reach each point based on total trip duration
- **Dynamic route sampling** — number of points scales with distance (1 point per 20km, min 5, max 25)
- **Efficient API usage** — fetches all weather data in a single Open-Meteo request
- **Clear recommendation** — returns `"Take an umbrella!"` or `"You're good to go!"`
- **Web interface** — clean, minimal frontend with EN/PT-BR language toggle
- **Rate limiting** — 10 requests per minute per IP to protect external API quotas
- **Input validation** — rejects empty, whitespace-only, or oversized inputs
- **Automated tests** — pytest suite with mocked external API calls
- **Secure config** — API keys managed via `.env` with `.env.example` provided

---

## Architecture
```
Will_It_Rain/
├── backend/
│   ├── geocoding.py     # Address → coordinates via LocationIQ
│   ├── http_client.py   # Shared async HTTP client
│   ├── main.py          # FastAPI app, endpoint definition and orchestration
│   ├── route.py         # Route calculation and point segmentation via OpenRouteService
│   └── weather.py       # Precipitation forecast via Open-Meteo
├── frontend/
│   ├── index.html       # Web interface
│   ├── style.css        # Styles
│   └── script.js        # API integration and DOM rendering
├── tests/
│   ├── __init__.py
│   └── test_main.py     # Endpoint and input validation tests
├── assets/
├── .env.example
└── .gitignore
```

Each backend module has a single responsibility. `main.py` orchestrates the pipeline; the other three are independent, testable services.

---

## Setup

**Prerequisites:**
- Python 3.13+
- Free API key from [LocationIQ](https://locationiq.com/)
- Free API key from [OpenRouteService](https://openrouteservice.org/)

**Install:**
```bash
git clone https://github.com/EduardoCassanha/Will-It-Rain-.git
cd Will_It_Rain
pip install -r requirements.txt
```

**Configure:**
```bash
cp .env.example .env
# Add your API keys to .env
```

**.env:**
```env
LOCATIONIQ_TOKEN=your_locationiq_token
ORS_API_KEY=your_ors_api_key
ALLOWED_ORIGINS=http://localhost:8000
```

**Run the API:**
```bash
python -m uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to explore and test the API via Swagger UI.

**Run the frontend:**
```bash
cd frontend
python -m http.server 5500
```

Open `http://localhost:5500` in your browser.

**Run tests:**
```bash
python -m pytest
```

---

## Usage

**`POST /check-rain`**
```json
{
  "origin": "Barueri, São Paulo",
  "destination": "Guarulhos, São Paulo",
  "departure_time": "2026-03-04T08:00"
}
```

`departure_time` is optional — if omitted, the current time is used.

**Response:**
```json
{
  "origin": "Barueri, São Paulo",
  "destination": "Guarulhos, São Paulo",
  "departure_time": "2026-03-04T08:00",
  "will_rain": false,
  "max_precipitation_probability": 12,
  "recommendation": "You're good to go!",
  "route_weather": [...]
}
```

---

## APIs Used

| Service | Purpose |
|---|---|
| [LocationIQ](https://locationiq.com/) | Geocoding — address to coordinates |
| [OpenRouteService](https://openrouteservice.org/) | Routing — path and duration |
| [Open-Meteo](https://open-meteo.com/) | Weather forecast — precipitation per point |

---

## Design Notes

- **Single weather request** — all forecast queries are batched into one Open-Meteo call to minimize latency and respect rate limits
- **Dynamic route points** — scales with distance: 1 point per 20km, minimum 5, maximum 25
- **Time estimation** — arrival time at each point is linearly interpolated from total trip duration; no real-time traffic data
- **Past date protection** — API rejects departure times more than 5 minutes in the past
- **Rate limit handling** — geocoding layer detects 429 responses from LocationIQ and returns a clean error upstream

---

## License

No license applied. All rights reserved.