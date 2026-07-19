import importlib
from fastapi.testclient import TestClient

# Using importlib to be able to import files that start with digits
app_module = importlib.import_module("src.04_alert_api")
client = TestClient(app_module.app)

def test_post_and_get_alerts():
    # Valid example 
    payload = {
        "package_id": 123,
        "transit_time_hours": 48.5,
        "anomaly_score": -0.8,
        "reason": "Test anomaly"
    }
    
    # Taking the test dictionary and sending it as a JSON to the /alerts endpoint
    response = client.post("/alerts", json=payload)
    # Checks that the API says "created sucesffully"
    assert response.status_code == 201

    # Ask the API to return the stored alerts 
    retrieved = client.get("/alerts")
    # See if retrieved successfully
    assert retrieved.status_code == 200

    assert len(retrieved.json()["alerts"]) == 1
    assert retrieved.json()["alerts"][0]["package_id"] == 123

def test_alert_cap_():
    """
    Tests GET /alerts to see if it returns exactly 50.
    """
    payload = {
        "package_id": 123,
        "transit_time_hours": 48.5,
        "anomaly_score": -0.8,
        "reason": "Test anomaly"
    }
    for i in range(59):
        response = client.post("/alerts", json=payload)

    retrieved = client.get("/alerts")
    assert retrieved.status_code == 200

    assert len(retrieved.json()["alerts"]) == 50
    