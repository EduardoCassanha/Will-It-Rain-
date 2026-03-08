import logging
import os
import httpx
from dotenv import load_dotenv

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
        "api_key": ORS_API_KEY,
        "start": f"{origin['lon']},{origin['lat']}",
        "end": f"{destination['lon']},{destination['lat']}"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            logger.info(f"ROUTE: Fetching route from {origin['name']} to {destination['name']}")
            response = await client.get(ORS_URL, headers=headers, params=params)

            if response.status_code != 200:
                return []

            response.raise_for_status()
            data = response.json()

            feature = data["features"][0]
            coordinates = feature["geometry"]["coordinates"]
            summary = feature["properties"]["summary"]

            duration_seconds = summary["duration"]
            distance_km = summary["distance"] / 1000

            ideal_points = int(distance_km / 20)
            num_points = max(5, min(ideal_points, 25))
            step = max(1, len(coordinates) // num_points)
            sampled = coordinates[::step]

            points = []
            num_sampled = len(sampled)

            for i, coord in enumerate(sampled):
                progress = i / (num_sampled - 1) if num_sampled > 1 else 0
                estimated_minutes = (duration_seconds * progress) / 60
                points.append({
                    "lat": coord[1],
                    "lon": coord[0],
                    "estimated_minutes": round(estimated_minutes, 2)
                })

            return points
        except Exception as e:
            logger.error(f"ROUTE: Error fetching route: {str(e)}")
            return []