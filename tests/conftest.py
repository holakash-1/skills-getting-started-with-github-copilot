import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


# Store the initial state of activities
INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Clear the activities dict
    activities.clear()
    # Restore initial state with deep copy to prevent test pollution
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield
    # No cleanup needed after test, next test will reset


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app"""
    return TestClient(app)
