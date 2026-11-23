from fastapi.testclient import TestClient
from app import app

client = TestClient(app)



def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200

    data = response.json()
    assert data["student_id"] == "FA23-BDS-060"
    assert data["accuracy"] > 0
    assert data["training_rows"] >= 100
    assert data["model_version"]
    assert data["git_sha"]


def test_predict():
    records = [{
        "pressure_loss": 0.5,
        "flow_change": 0.4,
        "valve_age": 0.7,
        "sensor_noise": 0.2
    }]

    response = client.post("/predict", json={"records": records})

    assert response.status_code == 200
    assert len(response.json()["predictions"]) == 1
    assert len(response.json()["probabilities"]) == 1
