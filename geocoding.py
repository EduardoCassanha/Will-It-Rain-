import requests

def get_coordinates(address: str) ->dict:
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format': 'json',
        'limit': 1
    }
    headers = {
        "User-Agent": "will-it-rain/1.0"
    }

    response = requests.get(url, params=params, headers=headers)
    results = response.json()

    if not results:
        return None

    location = results[0]
    return {
        "name": location["display_name"],
        "lat": float(location["lat"]),
        "lon": float(location["lon"])
    }