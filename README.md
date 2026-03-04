# Will It Rain? 🌧️

API that checks if it will rain along your route, so you know whether to take an umbrella.

## How it works

Given an origin and destination, the API:
1. Converts addresses to coordinates (Nominatim)
2. Calculates the route (OpenRouteService)
3. Checks the weather at each point along the route (Open-Meteo)
4. Returns a recommendation based on precipitation probability

## Setup

1. Clone the repository
2. Install dependencies:
```
   pip install fastapi uvicorn requests python-dotenv
```
3. Create a `.env` file based on `.env.example` and add your API key
4. Run the server:
```
   python -m uvicorn main:app --reload
```
5. Open `http://127.0.0.1:8000/docs` to test the API

## Usage

**POST** `/check-rain`
```json
{
  "origin": "Barueri, São Paulo",
  "destination": "Guarulhos, São Paulo",
  "departure_time": "2026-03-04T08:00"
}
```

## APIs used

- [Nominatim](https://nominatim.openstreetmap.org/) — Geocoding
- [OpenRouteService](https://openrouteservice.org/) — Routing
- [Open-Meteo](https://open-meteo.com/) — Weather forecast
```

E o **.env.example:**
```
ORS_API_KEY=your_key_here