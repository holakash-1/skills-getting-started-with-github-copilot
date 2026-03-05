"""
Unit tests for the Mergington High School API

Tests are organized by endpoint and include edge case validation.
The reset_activities fixture (from conftest.py) ensures a clean state before each test.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app"""
    return TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client):
        """Test that endpoint returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that response is a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_all_activities_present(self, client):
        """Test that all three activities are present"""
        response = client.get("/activities")
        activities = response.json()
        
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = {"description", "schedule", "max_participants", "participants"}
        for activity_name, activity in activities.items():
            assert required_fields.issubset(activity.keys()), \
                f"Activity '{activity_name}' missing required fields"
    
    def test_participants_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity in activities.items():
            assert isinstance(activity["participants"], list), \
                f"Activity '{activity_name}' participants is not a list"
    
    def test_initial_participant_counts(self, client):
        """Test initial participant counts for each activity"""
        response = client.get("/activities")
        activities = response.json()
        
        assert len(activities["Chess Club"]["participants"]) == 2
        assert len(activities["Programming Class"]["participants"]) == 2
        assert len(activities["Gym Class"]["participants"]) == 2
    
    def test_activity_structure_chess_club(self, client):
        """Test structure and content of Chess Club activity"""
        response = client.get("/activities")
        chess = response.json()["Chess Club"]
        
        assert chess["max_participants"] == 12
        assert "michael@mergington.edu" in chess["participants"]
        assert "daniel@mergington.edu" in chess["participants"]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_to_existing_activity_returns_200(self, client):
        """Test successful signup to an existing activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
    
    def test_signup_returns_success_message(self, client):
        """Test that successful signup returns appropriate message"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "alice@mergington.edu"}
        )
        data = response.json()
        assert "message" in data
        assert "alice@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """Test signup to non-existent activity returns 404"""
        response = client.post(
            "/activities/Dance Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_signup_nonexistent_activity_error_message(self, client):
        """Test that 404 error message is appropriate"""
        response = client.post(
            "/activities/Theater Club/signup",
            params={"email": "student@mergington.edu"}
        )
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_participant_added_to_activity(self, client):
        """Test that participant is actually added to the activity"""
        email = "testuser@mergington.edu"
        
        # Sign up
        client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Programming Class"]["participants"]
    
    def test_multiple_signups_to_different_activities(self, client):
        """Test that a user can sign up for multiple activities"""
        email = "versatile@mergington.edu"
        
        # Sign up for Chess Club
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Sign up for Gym Class
        client.post(
            "/activities/Gym Class/signup",
            params={"email": email}
        )
        
        # Verify both signups
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Gym Class"]["participants"]
    
    def test_signup_increases_participant_count(self, client):
        """Test that signup increases the participant count"""
        email = "counter@mergington.edu"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Sign up
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Get new count
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        
        assert new_count == initial_count + 1
    
    def test_duplicate_signup_allowed(self, client):
        """Test that duplicate signups are currently allowed (edge case)
        
        NOTE: This test documents the current behavior where duplicate
        signups are permitted. This could be a potential enhancement
        to prevent duplicate signups in the future.
        """
        email = "duplicate@mergington.edu"
        
        # First signup
        response1 = client.post(
            "/activities/Gym Class/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup (duplicate)
        response2 = client.post(
            "/activities/Gym Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both entries exist
        response = client.get("/activities")
        participants = response.json()["Gym Class"]["participants"]
        assert participants.count(email) == 2
    
    def test_signup_with_various_email_formats(self, client):
        """Test that signup accepts various email string formats
        
        NOTE: The API currently doesn't validate email format,
        so any string is accepted as an email parameter.
        """
        test_emails = [
            "simple@example.com",
            "user+tag@school.edu",
            "firstname.lastname@institution.org",
            "notarealemail",  # No validation
            "user@localhost"
        ]
        
        for email in test_emails:
            response = client.post(
                "/activities/Chess Club/signup",
                params={"email": email}
            )
            assert response.status_code == 200
    
    def test_signup_respects_activity_name_case_sensitivity(self, client):
        """Test that activity names are case-sensitive"""
        response = client.post(
            "/activities/chess club/signup",  # lowercase
            params={"email": "test@mergington.edu"}
        )
        # Should fail because exact name "Chess Club" is required
        assert response.status_code == 404
    
    def test_signup_with_missing_email_parameter(self, client):
        """Test signup with missing email parameter"""
        response = client.post(
            "/activities/Chess Club/signup"
        )
        # FastAPI should return 422 for missing required parameter
        assert response.status_code == 422
    
    def test_capacity_limits_currently_not_enforced(self, client):
        """Test that max_participants limits are currently not enforced
        
        NOTE: This test documents the current behavior where capacity
        limits are defined but not enforced. This could be an enhancement
        to validate signup counts against max_participants.
        """
        # Chess Club has max_participants = 12, currently has 2
        # Try to sign up 20 more people (exceeding limit)
        for i in range(20):
            response = client.post(
                "/activities/Chess Club/signup",
                params={"email": f"student{i}@mergington.edu"}
            )
            assert response.status_code == 200
        
        # Verify all were added despite exceeding max_participants
        response = client.get("/activities")
        chess_participants = response.json()["Chess Club"]["participants"]
        assert len(chess_participants) > 12  # More than max_participants
