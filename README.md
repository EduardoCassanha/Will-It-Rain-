# Will It Rain? 🌧️

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)
![Status](https://img.shields.io/badge/Status-Functional-brightgreen?style=flat)

> **Don't just check the weather at your destination. Check it along the way.**

A REST API that tells you whether it will rain **during your journey** — not just at your destination. Given an origin, destination, and departure time, it maps your route, estimates when you'll reach each point, and checks the forecast at the right time for each location.

---

## The Problem

Most weather apps check a single location at a single time. But if you're driving 2 hours across the city, rain at your destination in 30 minutes doesn't mean you'll get wet — and clear skies now doesn't mean you'll stay dry. **Will It Rain?** solves this by treating your route as a timeline, not a single point.

---

## How It Works

```
Origin + Destination + Departure Time
          ↓
  Geocoding (Nominatim)
  Converts addresses → coordinates
          ↓
  Routing (OpenRouteService)
  Calculates full route + total duration
          ↓
  Route Segmentation
  Splits route into up to 10 points
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
- **Efficient API usage** — fetches all weather data in a single Open-Meteo request
- **Clear recommendation** — returns `"Take an umbrella!"` or `"You're good to go!"`
- **Secure config** — API keys managed via `.env` with `.env.example` provided

---

## Architecture

```
will-it-rain/
├── main.py          # FastAPI app, endpoint definition and orchestration
├── geocoding.py     # Address → coordinates via Nominatim
├── route.py         # Route calculation and point segmentation via OpenRouteService
├── weather.py       # Precipitation forecast via Open-Meteo
├── .env.example     # Environment variable template
└── .gitignore
```

Each module has a single responsibility. `main.py` orchestrates the pipeline; the other three are independent, testable services.

---

## Setup

**Prerequisites:**
- Python 3.11+
- Free API key from [OpenRouteService](https://openrouteservice.org/)

**Install:**

```bash
git clone https://github.com/EduardoCassanha/will-it-rain.git
cd will-it-rain
pip install fastapi uvicorn requests python-dotenv
```

**Configure:**

```bash
cp .env.example .env
# Add your OpenRouteService API key to .env
```

**Run:**

```bash
python -m uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` to explore and test the API via Swagger UI.

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

**Response:**

```json
{
  "will_rain": false,
  "max_precipitation_probability": 12,
  "recommendation": "You're good to go!"
}
```

---

## APIs Used

| Service | Purpose |
|---|---|
| [Nominatim](https://nominatim.org/) | Geocoding — address to coordinates |
| [OpenRouteService](https://openrouteservice.org/) | Routing — path and duration |
| [Open-Meteo](https://open-meteo.com/) | Weather forecast — precipitation per point |

---

## Design Notes

- **Single weather request** — all forecast queries are batched into one Open-Meteo call to minimize latency and respect rate limits
- **Up to 10 route points** — balances forecast accuracy with API efficiency
- **Time estimation** — arrival time at each point is linearly interpolated from total trip duration; no real-time traffic data

---

## License

This project is licensed under the MIT License.