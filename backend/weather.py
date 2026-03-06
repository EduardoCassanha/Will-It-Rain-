import requests
from datetime import datetime, timedelta

def get_weather_for_points(points: list, departure_time: str) -> list:
    base_time = datetime.fromisoformat(departure_time)

    latitudes = [str(p["lat"]) for p in points]
    longitudes = [str(p["lon"]) for p in points]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": ",".join(latitudes),
        "longitude": ",".join(longitudes),
        "hourly": "precipitation_probability,precipitation",
        "timezone": "America/Sao_Paulo",
        "forecast_days": 2
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, list):
        data = [data]

    results = []
    for i, point in enumerate(points):
        arrival = base_time + timedelta(minutes=point["estimated_minutes"])
        hour_str = arrival.strftime("%Y-%m-%dT%H:00")

        hourly = data[i]["hourly"]
        times = hourly["time"]
        prec_prob = hourly["precipitation_probability"]
        prec = hourly["precipitation"]

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