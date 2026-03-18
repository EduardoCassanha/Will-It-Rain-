import logging
import os
from dotenv import load_dotenv
from backend.http_client import http_client

load_dotenv()
logger = logging.getLogger(__name__)

ORS_API_KEY = os.getenv("ORS_API_KEY")
ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"


async def get_route(origin: dict, destination: dict) -> list[dict]:
    if not ORS_API_KEY:
        logger.error("ROUTE: ORS_API_KEY missing in .env")
        return []

    headers = {
        "Authorization": ORS_API_KEY,
        "User-Agent": "WillItRain/1.0 (https://github.com/EduardoCassanha/Will-It-Rain-)"
    }

    params = {
        "start": f"{origin['lon']},{origin['lat']}",
        "end": f"{destination['lon']},{destination['lat']}"
    }

    try:
        logger.info(f"ROUTE: Fetching route from {origin['name']} to {destination['name']}")

        response = await http_client.get(ORS_URL, headers=headers, params=params)

        if response.status_code != 200:
            return []

        data = response.json()

        features = data.get("features")
        if not features:
            logger.warning(f"ROUTE: No route found between {origin['name']} and {destination['name']}")
            return []
        feature = features[0]

        geometry = feature.get("geometry", {})
        properties = feature.get("properties", {})

        coordinates = geometry.get("coordinates", [])
        summary = properties.get("summary", {})

        if not coordinates or not summary:
            logger.warning(f"ROUTE: Incomplete data (coords/summary) for route to {destination['name']}")
            return []

        duration_seconds = summary.get("duration", 0)
        distance_km = summary.get("distance", 0) / 1000

        ideal_points = int(distance_km / 20)
        num_points = max(5, min(ideal_points, 25))

        total_coords = len(coordinates)
        step = max(1, total_coords // num_points)

        sampled = coordinates[::step]

        if total_coords > 0 and coordinates[-1] not in sampled:
            sampled.append(coordinates[-1])

        points = []
        num_sampled = len(sampled)

        for i, coord in enumerate(sampled):
            progress = i / (num_sampled - 1) if num_sampled > 1 else 1.0
            estimated_minutes = (duration_seconds * progress) / 60

            points.append({
                "lat": coord[1],
                "lon": coord[0],
                "estimated_minutes": round(estimated_minutes, 2)
            })

        return points
    except Exception:
        logger.error(f"ROUTE: Error fetching route")
        return []