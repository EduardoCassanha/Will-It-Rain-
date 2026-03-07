import requests
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()
API_KEY = os.getenv("ORS_API_KEY")

def get_route(origin: dict, destination: dict) -> list:

    if not API_KEY:
        return []

    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": API_KEY,
        "User-Agent": "WillItRain/1.0 (https://github.com/EduardoCassanha/Will-It-Rain-)"
    }

    params = {
        "start": f"{origin['lon']},{origin['lat']}",
        "end": f"{destination['lon']},{destination['lat']}"
    }

    try:

        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if "features" not in data or not data["features"]:
            return []

        coordinates = data["features"][0]["geometry"]["coordinates"]
        duration_seconds = data["features"][0]["properties"]["summary"]["duration"]

        step = max(1, len(coordinates) // 10)
        sampled = coordinates[::step]

        points = []
        for i, coord in enumerate(sampled):
            points.append({
                "lat": coord[1],
                "lon": coord[0],
                "estimated_minutes": (duration_seconds / len(sampled)) * i / 60
            })

        return points

    except (requests.RequestException, KeyError, IndexError):
        return []