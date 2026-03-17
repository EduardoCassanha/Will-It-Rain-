from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

client = TestClient(app)

@patch("backend.main.get_coordinates", new_callable=AsyncMock)
@patch("backend.main.get_route", new_callable=AsyncMock)
@patch("backend.main.get_weather_for_points", new_callable=AsyncMock)
def test_check_rain_success(mock_weather, mock_route, mock_coords):
    mock_coords.return_value = {"name": "São Paulo", "lat": -23.55, "lon": -46.63}
    mock_route.return_value = [{"lat": -23.55, "lon": -46.63, "estimated_minutes": 0}]
    future_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M")
    mock_weather.return_value = [{"precipitation_probability": 20, "precipitation_mm": 0, "lat": -23.55, "lon": -46.63, "time": future_time}]

    response = client.post("/check-rain", json={"origin": "São Paulo", "destination": "Campinas"})
    assert response.status_code == 200
    assert "will_rain" in response.json()

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_check_rain_missing_fields():
    response = client.post("/check-rain", json={})
    assert response.status_code == 422

def test_check_rain_empty_origin():
    response = client.post("/check-rain", json={"origin": "", "destination": "Campinas"})
    assert response.status_code == 422

def test_check_rain_input_too_long():
    response = client.post("/check-rain", json={"origin": "a" * 201, "destination": "Campinas"})
    assert response.status_code == 422