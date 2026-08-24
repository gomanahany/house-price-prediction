from fastapi.testclient import TestClient
from app.main import app

VALID_PAYLOAD = {"location": "other", "carpet_area_sqft": 800, "floor_num": 3, "bathroom": 2, "balcony": 1, "car_parking": 1, "furnishing": "Semi-Furnished", "transaction": "Resale", "ownership": "Freehold", "facing": "East"}

def test_valid_prediction_returns_a_price():
    with TestClient(app) as client:
        response = client.post("/predict", json=VALID_PAYLOAD)
    assert response.status_code == 200
    assert response.json()["predicted_price"] > 0

def test_invalid_area_returns_422():
    with TestClient(app) as client:
        response = client.post("/predict", json={**VALID_PAYLOAD, "carpet_area_sqft": 0})
    assert response.status_code == 422
