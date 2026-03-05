import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Based on the current activities
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_valid():
    response = client.post("/activities/Chess Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]

    # Verify added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Chess Club"]["participants"]


def test_signup_duplicate():
    # First signup
    client.post("/activities/Chess Club/signup?email=duplicate@example.com")
    # Second signup
    response = client.post("/activities/Chess Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_invalid_activity():
    response = client.post("/activities/Invalid Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]


def test_delete_valid():
    # First signup
    client.post("/activities/Basketball/signup?email=delete@example.com")
    # Then delete
    response = client.delete("/activities/Basketball/signup?email=delete@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "delete@example.com" in data["message"]

    # Verify removed
    response = client.get("/activities")
    data = response.json()
    assert "delete@example.com" not in data["Basketball"]["participants"]


def test_delete_not_signed_up():
    response = client.delete("/activities/Tennis Club/signup?email=notsigned@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]


def test_delete_invalid_activity():
    response = client.delete("/activities/Invalid Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]


def test_get_root_redirect():
    response = client.get("/")
    assert response.status_code == 200  # TestClient follows redirect
    assert "Mergington High School Activities" in response.text