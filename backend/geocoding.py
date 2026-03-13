import os
import httpx
import logging
from typing import Optional
from dotenv import load_dotenv
from backend.http_client import http_client

load_dotenv()
logger = logging.getLogger(__name__)

LIQ_TOKEN = os.getenv("LOCATIONIQ_TOKEN")
LIQ_BASE_URL = "https://us1.locationiq.com/v1/search"

async def get_coordinates(address: str) -> Optional[dict]:
    if not LIQ_TOKEN:
        logger.error("GEOCODING: LOCATIONIQ_TOKEN missing in environment")
        return None

    params = {
        'key': LIQ_TOKEN,
        'q': address,
        'format': "json",
        'limit': 1
    }
    headers = {
        "User-Agent": "WillItRain/1.0 (https://github.com/EduardoCassanha/Will-It-Rain-)"
    }

    try:
        logger.info(f"GEOCODING: Searching coordinates for {address}")

        response = await http_client.get(LIQ_BASE_URL, params=params, headers=headers)

        if response.status_code == 429:
            logger.warning(f"GEOCODING: Rate limit reached for LocationIQ | Query: {address}")
            return None

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
        logger.error(f"GEOCODING: Request failed | Query: {address} | Error: '{str(e)}'")
        return None