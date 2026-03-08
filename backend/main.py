import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
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
async def root():
    return {"message": "Will It Rain API is on!"}

@app.post("/check-rain")
async def check_rain(trip: TripRequest):
    now = datetime.now()

    if not trip.departure_time or trip.departure_time.strip() == "":
        departure = now.strftime("%Y-%m-%dT%H:00")
    else:
        try:
            dt_departure = datetime.fromisoformat(trip.departure_time)
            if dt_departure < (now - timedelta(minutes=5)):
                raise HTTPException(
                    status_code=400,
                    detail="Departure date cannot be in the past."
                )
            departure = trip.departure_time
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format.")


    origin_task = get_coordinates(trip.origin)
    dest_task = get_coordinates(trip.destination)

    origin_coords, destination_coords = await asyncio.gather(origin_task, dest_task)

    if not origin_coords or not destination_coords:
        raise HTTPException(status_code=404, detail="Could not find one or both locations.")

    route_points = await get_route(origin_coords, destination_coords)

    if not route_points:
        raise HTTPException(
            status_code=422,
            detail="No ground route found between these locations."
        )

    try:
        weather = get_weather_for_points(route_points, departure)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Weather service unavailable: {str(e)}")

    if not weather:
        raise HTTPException(status_code=422, detail="Could not calculate route weather.")

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