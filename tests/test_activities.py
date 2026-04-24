import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_includes_activity_details(self, client, reset_activities):
        """Test that activities include all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert chess_club["description"]
        assert chess_club["schedule"]
        assert chess_club["max_participants"] == 12
        assert isinstance(chess_club["participants"], list)
        assert len(chess_club["participants"]) == 2


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client, reset_activities):
        """Test signing up a new participant for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_increases_participant_count(self, client, reset_activities):
        """Test that signup increases the participant count"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Signup a new participant
        client.post(
            "/activities/Chess%20Club/signup?email=new@mergington.edu"
        )
        
        # Verify count increased
        response = client.get("/activities")
        final_count = len(response.json()["Chess Club"]["participants"])
        assert final_count == initial_count + 1
    
    def test_signup_duplicate_participant_rejected(self, client, reset_activities):
        """Test that duplicate signups are rejected"""
        # Try to signup someone already signed up
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_with_various_email_formats(self, client, reset_activities):
        """Test signup with different valid email formats"""
        emails = [
            "student1@mergington.edu",
            "john.doe@mergington.edu",
            "test+alias@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/Programming%20Class/signup?email={email}"
            )
            assert response.status_code == 200
    
    def test_signup_response_contains_correct_message(self, client, reset_activities):
        """Test that signup response contains appropriate message"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=alice@mergington.edu"
        )
        data = response.json()
        assert "Signed up" in data["message"]
        assert "alice@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "michael@mergington.edu" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_decreases_participant_count(self, client, reset_activities):
        """Test that unregister decreases the participant count"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Unregister a participant
        client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        # Verify count decreased
        response = client.get("/activities")
        final_count = len(response.json()["Chess Club"]["participants"])
        assert final_count == initial_count - 1
    
    def test_unregister_nonexistent_participant_returns_400(self, client, reset_activities):
        """Test that unregistering non-existent participant returns 400"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        assert "Participant not found" in response.json()["detail"]
    
    def test_unregister_from_nonexistent_activity_returns_404(self, client, reset_activities):
        """Test that unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_response_contains_correct_message(self, client, reset_activities):
        """Test that unregister response contains appropriate message"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=daniel@mergington.edu"
        )
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "daniel@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_unregister_allows_same_participant_to_signup_again(self, client, reset_activities):
        """Test that unregistered participants can signup again"""
        # Unregister
        client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        # Signup again
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200


class TestSignupAndUnregisterWorkflow:
    """Integration tests for signup and unregister workflows"""
    
    def test_signup_unregister_signup_workflow(self, client, reset_activities):
        """Test complete workflow: signup -> unregister -> signup again"""
        email = "workflow@mergington.edu"
        activity = "Programming%20Class"
        
        # Initial signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response2.status_code == 200
        
        # Signup again
        response3 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response3.status_code == 200
    
    def test_multiple_participants_signup_and_unregister(self, client, reset_activities):
        """Test multiple participants signing up and unregistering"""
        participants = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        activity = "Programming%20Class"
        
        # All signup
        for email in participants:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all enrolled
        response = client.get("/activities")
        enrolled = response.json()[activity.replace("%20", " ")]["participants"]
        for email in participants:
            assert email in enrolled
        
        # Unregister one
        client.delete(f"/activities/{activity}/unregister?email={participants[0]}")
        
        # Verify count updated
        response = client.get("/activities")
        enrolled = response.json()[activity.replace("%20", " ")]["participants"]
        assert participants[0] not in enrolled
        assert participants[1] in enrolled
        assert participants[2] in enrolled
    
    def test_participant_signup_different_activities(self, client, reset_activities):
        """Test same participant signing up for multiple activities"""
        email = "multi@mergington.edu"
        
        # Signup for Chess Club
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Signup for Programming Class
        response2 = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify enrolled in both
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]
