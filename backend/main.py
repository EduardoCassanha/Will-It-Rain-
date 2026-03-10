import asyncio
import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.http_client import http_client

load_dotenv()

from backend.geocoding import get_coordinates
from backend.route import get_route
from backend.weather import get_weather_for_points

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await http_client.aclose()
    logging.info("Global HTTP client closed.")
app = FastAPI(lifespan=lifespan)

raw_origins = os.getenv("ALLOWED_ORIGINS")

if raw_origins:
    origins = raw_origins.split(",")
else:
    origins = [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://localhost:63342"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

class TripRequest(BaseModel):
    origin: str
    destination: str
    departure_time: Optional[datetime] = None

@app.get("/")
async def root():
    return {"message": "Will It Rain API is on!"}

@app.post("/check-rain")
async def check_rain(trip: TripRequest):
    now = datetime.now()

    departure = trip.departure_time or now
    if departure < (now - timedelta(minutes=5)):
        raise HTTPException(status_code=400, detail="Departure date cannot be in the past.")

    origin_coords, destination_coords = await asyncio.gather(
        get_coordinates(trip.origin),
        get_coordinates(trip.destination)
    )

    if not origin_coords or not destination_coords:
        raise HTTPException(status_code=404, detail="Could not find one or both locations.")

    route_points = await get_route(origin_coords, destination_coords)

    if not route_points:
        raise HTTPException(status_code=422, detail="No ground route found between these locations.")

    weather = await get_weather_for_points(route_points, departure.isoformat())

    if not weather:
        raise HTTPException(status_code=422, detail="Weather data unavailable.")

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