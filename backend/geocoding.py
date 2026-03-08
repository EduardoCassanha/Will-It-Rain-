import httpx
import logging
from typing import Optional

logger= logging.getLogger(__name__)

async def get_coordinates(address: str) -> Optional[dict]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'limit': 1,
        'addressdetails': 1
    }
    headers = {
        "User-Agent": "WillItRain/1.0 (https://github.com/EduardoCassanha/Will-It-Rain-)"
    }

    try:
        logger.info(f"GEOCODING: Searching coordinates for {address}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            results = response.json()

        if not results:
            logger.warning(f"GEOCODING: No results found for {address}")
            return None

        location = results[0]
        logger.info(f"GEOCODING: Found location for {address}")
        return {
            "name": location["display_name"],
            "lat": float(location["lat"]),
            "lon": float(location["lon"])
        }
    except httpx.HTTPError as e:
        logger.error(f"GEOCODING: Request failed | Query: {address}) | Error: '{str(e)}'")
        return None