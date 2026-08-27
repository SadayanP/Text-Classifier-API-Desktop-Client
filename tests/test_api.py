import os
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import DATABASE_PATH

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    """Remove the database and recreate tables before each test."""
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)

    from backend.database import create_tables
    create_tables()

    yield

    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        
        
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_login_classify_feedback():
    # Register
    register = client.post(
        "/register",
        json={"username": "testuser", "password": "testpass123"},
    )
    assert register.status_code == 200
    assert "id" in register.json()
    assert register.json()["username"] == "testuser"

    # Login
    login = client.post(
        "/login",
        json={"username": "testuser", "password": "testpass123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Classify
    classify = client.post(
        "/classify",
        headers=headers,
        json={"text": "I love this project"},
    )
    assert classify.status_code == 200
    data = classify.json()
    assert data["label"] in ["POSITIVE", "NEGATIVE"]
    assert "prediction_id" in data
    assert "confidence" in data
    prediction_id = data["prediction_id"]

    # Feedback
    feedback = client.post(
        "/feedback",
        headers=headers,
        json={"prediction_id": prediction_id, "is_correct": True},
    )
    assert feedback.status_code == 200
    assert feedback.json()["feedback"] is True
    assert feedback.json()["prediction_id"] == prediction_id


def test_classify_without_token():
    response = client.post(
        "/classify",
        json={"text": "This should fail"},
    )
    assert response.status_code == 401