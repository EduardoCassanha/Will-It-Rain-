import logging
from datetime import datetime, timedelta, timezone
from backend.http_client import http_client

logger = logging.getLogger(__name__)

async def get_weather_for_points(points: list, departure_time: str) -> list[dict]:
    MAX_POINTS = 50
    if not points or len(points) > MAX_POINTS:
        if points and len(points) > MAX_POINTS:
            logger.warning(f"WEATHER: Rejected. {len(points)} points exceeds MAX_POINTS {MAX_POINTS}")
        return []

    try:
        base_time = datetime.fromisoformat(departure_time).replace(tzinfo=timezone.utc)
        latitudes = [str(p["lat"]) for p in points]
        longitudes = [str(p["lon"]) for p in points]

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": ",".join(latitudes),
            "longitude": ",".join(longitudes),
            "hourly": "precipitation_probability,precipitation",
            "timezone": "UTC",
            "forecast_days": 2
        }

        headers = {"User-Agent": "WillItRain/1.0 (https://github.com/EduardoCassanha/Will-It-Rain-)"}

        response = await http_client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            data = [data]

        results = []
        for i, point in enumerate(points):

            if i >= len(data):
                continue

            arrival = base_time + timedelta(minutes=point["estimated_minutes"])
            hourly = data[i].get("hourly", {})

            prob_list = hourly.get("precipitation_probability", [])
            precip_list = hourly.get("precipitation", [])
            times = hourly.get("time", [])

            if not all([times, prob_list, precip_list]):
                logger.warning(f"WEATHER: Incomplete data for point {i} ({point['lat']}, {point['lon']})")
                continue

            try:

                api_times = [datetime.fromisoformat(t).replace(tzinfo=timezone.utc) for t in times]
                idx = min(range(len(api_times)), key=lambda j: abs(api_times[j] - arrival))

                results.append({
                    "lat": point["lat"],
                    "lon": point["lon"],
                    "time": times[idx],
                    "precipitation_probability": prob_list[idx],
                    "precipitation_mm": precip_list[idx],
                })
            except (ValueError, IndexError):
                continue

        return results
    except Exception as e:
        logger.error(f"Weather Service Error: {type(e).__name__}: {e}")
        return []