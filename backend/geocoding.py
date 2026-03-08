import requests
from typing import Optional

def get_coordinates(address: str) -> Optional[dict]:
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
        print(f"[INFO] GEOCODING: Searching coordinates for {address}")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json()

        if not results:
            print(f"[WARNING] GEOCODING: No results found for {address}")
            return None

        location = results[0]
        print(f"[SUCCESS] GEOCODING: Found location for {address}")
        return {
            "name": location["display_name"],
            "lat": float(location["lat"]),
            "lon": float(location["lon"])
        }
    except requests.RequestException as e:
        status_code = e.response.status_code if e.response else "Timeout/Network Error"
        print(f"[ERROR] GEOCODING: Request failed (Status: {status_code}) | Query: '{address}'")
        return None