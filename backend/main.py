import asyncio
import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.trustedhost import TrustedHostMiddleware

load_dotenv()

ENV = os.getenv("ENV", "development").lower()

from backend.geocoding import get_coordinates
from backend.http_client import http_client
from backend.route import get_route
from backend.weather import get_weather_for_points

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logging.getLogger("httpx").setLevel(logging.WARNING)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await http_client.aclose()
    logging.info("Global HTTP client closed.")

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    lifespan=lifespan,
    docs_url=None if ENV == "production" else "/docs",
    redoc_url=None if ENV == "production" else "/redoc",
    openapi_url=None if ENV == "production" else "/openapi.json"
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=[],
)

raw_hosts = os.getenv("ALLOWED_HOSTS")
allowed_hosts = raw_hosts.split(",") if raw_hosts else ["localhost", "127.0.0.1"]

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts,
)

class TripRequest(BaseModel):
    origin: str
    destination: str
    departure_time: Optional[datetime] = None

    @field_validator('origin', 'destination')
    @classmethod
    def validate_length(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be empty")
        if len(v) > 200:
            raise ValueError('Field too long')
        return v

@app.get("/")
async def root():
    return {"message": "Will It Rain API is on!"}

@app.post("/check-rain")
@limiter.limit("10/minute")
async def check_rain(request: Request, trip: TripRequest):
    now = datetime.now(timezone.utc)

    departure = trip.departure_time or now
    if departure < (now - timedelta(minutes=5)):
        raise HTTPException(status_code=400, detail="Departure date cannot be in the past.")

    origin_coords, destination_coords = await asyncio.gather(
        get_coordinates(trip.origin),
        get_coordinates(trip.destination)
    )

    if not origin_coords:
        raise HTTPException(status_code=404, detail=f"Origin '{trip.origin}' not found.")
    if not destination_coords:
        raise HTTPException(status_code=404, detail=f"Destination '{trip.destination}' not found.")

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