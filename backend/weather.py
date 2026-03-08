import httpx
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

async def get_weather_for_points(points: list, departure_time: str) -> list[dict]:
    if not points:
        return []

    try:
        base_time = datetime.fromisoformat(departure_time)
        latitudes = [str(p["lat"]) for p in points]
        longitudes = [str(p["lon"]) for p in points]

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": ",".join(latitudes),
            "longitude": ",".join(longitudes),
            "hourly": "precipitation_probability,precipitation",
            "timezone": "auto",
            "forecast_days": 2
        }

        headers = {"User-Agent": "WillItRain/1.0 (https://github.com/EduardoCassanha/Will-It-Rain-)"}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

        if not isinstance(data, list):
            data = [data]

        results = []
        for i, point in enumerate(points):
            arrival = base_time + timedelta(minutes=point["estimated_minutes"])
            hour_str = arrival.strftime("%Y-%m-%dT%H:00")

            if i >= len(data):
                continue

            hourly = data[i].get("hourly", {})
            times = hourly.get("time", [])
            prec_prob = hourly.get("precipitation_probability", [])
            prec = hourly.get("precipitation", [])

            if hour_str in times:
                idx = times.index(hour_str)
                results.append({
                    "lat": point["lat"],
                    "lon": point["lon"],
                    "time": hour_str,
                    "precipitation_probability": prec_prob[idx],
                    "precipitation_mm": prec[idx]
                })

        return results
    except Exception as e:
        logger.error(f"Weather Service Error: {e}")
        return []