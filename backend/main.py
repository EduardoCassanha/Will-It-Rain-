from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from backend.geocoding import get_coordinates
from backend.route import get_route
from backend.weather import get_weather_for_points

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TripRequest(BaseModel):
    origin: str
    destination: str
    departure_time: Optional[str] = None

@app.get("/")
def root():
    return {"message": "Will It Rain API is on!"}

@app.post("/check-rain")
def check_rain(trip: TripRequest):
    departure = trip.departure_time or datetime.now().strftime("%Y-%m-%dT%H:00")

    origin_coords = get_coordinates(trip.origin)
    destination_coords = get_coordinates(trip.destination)

    if not origin_coords or not destination_coords:
        return {"error": "Could not find one or both locations."}

    route_points = get_route(origin_coords, destination_coords)

    try:
        weather = get_weather_for_points(route_points, departure)
    except Exception as e:
        return {"error": f"Weather service unavailable: {str(e)}"}

    if not weather:
        return {"error": "Could not calculate route weather."}

    max_prob = max((w.get("precipitation_probability", 0) for w in weather), default=0)
    will_rain = max_prob >= 40

    return {
        "origin": trip.origin,
        "destination": trip.destination,
        "departure_time": departure,
        "will_rain": will_rain,
        "max_precipitation_probability": max_prob,
        "recommendation": "Take an umbrella!" if will_rain else "You're good to go!",
        "route_weather": weather
    }