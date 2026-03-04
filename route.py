import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("ORS_API_KEY")

def get_route(origin: dict, destination: dict) -> list:
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        "Authorization": API_KEY
    }
    params = {
        "start": f"{origin['lon']},{origin['lat']}",
        "end": f"{destination['lon']},{destination['lat']}"
    }

    response = requests.get(url, headers=headers, params=params)
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