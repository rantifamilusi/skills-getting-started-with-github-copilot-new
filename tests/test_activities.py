import pytest
from fastapi import HTTPException


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities with correct structure"""
        # Arrange
        expected_activity_names = ["Chess Club", "Programming Class", "Full Activity"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert set(data.keys()) == set(expected_activity_names)
        assert all("description" in data[name] for name in expected_activity_names)
        assert all("schedule" in data[name] for name in expected_activity_names)
        assert all("max_participants" in data[name] for name in expected_activity_names)
        assert all("participants" in data[name] for name in expected_activity_names)
    
    def test_get_activities_returns_correct_participant_counts(self, client, reset_activities):
        """Test that participant lists are accurate"""
        # Arrange
        # (activities already set up in fixture)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert len(data["Chess Club"]["participants"]) == 1
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert len(data["Programming Class"]["participants"]) == 0
        assert len(data["Full Activity"]["participants"]) == 1


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_successfully(self, client, reset_activities):
        """Test successfully signing up a new student"""
        # Arrange
        activity_name = "Programming Class"
        email = "alice@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in reset_activities[activity_name]["participants"]
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity returns 404"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_student_already_registered(self, client, reset_activities):
        """Test signup fails when student already signed up"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_activity_is_full(self, client, reset_activities):
        """Test signup fails when activity has no spots"""
        # Arrange
        activity_name = "Full Activity"
        email = "new@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Activity is full"
    
    def test_signup_last_available_spot(self, client, reset_activities):
        """Test signing up when only 1 spot remains"""
        # Arrange
        activity_name = "Chess Club"  # max_participants=2, current=1
        email = "david@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in reset_activities[activity_name]["participants"]
        assert len(reset_activities[activity_name]["participants"]) == 2
    
    def test_signup_updates_participant_list(self, client, reset_activities):
        """Test that participant list is updated correctly after signup"""
        # Arrange
        activity_name = "Programming Class"
        new_emails = ["alice@mergington.edu", "bob@mergington.edu"]
        
        # Act
        for email in new_emails:
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
        
        # Assert
        participants = reset_activities[activity_name]["participants"]
        assert len(participants) == 2
        for email in new_emails:
            assert email in participants


class TestRemoveFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_remove_participant_successfully(self, client, reset_activities):
        """Test successfully removing a participant"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(reset_activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email not in reset_activities[activity_name]["participants"]
        assert len(reset_activities[activity_name]["participants"]) == initial_count - 1
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
    
    def test_remove_activity_not_found(self, client, reset_activities):
        """Test remove from non-existent activity returns 404"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_remove_student_not_signed_up(self, client, reset_activities):
        """Test remove fails when student not signed up"""
        # Arrange
        activity_name = "Programming Class"  # No participants
        email = "unknown@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not signed up for this activity"


class TestSignupRemoveIntegration:
    """Integration tests for signup and remove workflows"""
    
    def test_signup_then_remove_workflow(self, client, reset_activities):
        """Test complete workflow: signup → verify added → remove → verify removed"""
        # Arrange
        activity_name = "Programming Class"
        email = "integration@mergington.edu"
        
        # Act: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Signed up successfully
        assert signup_response.status_code == 200
        assert email in reset_activities[activity_name]["participants"]
        
        # Act: Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Removed successfully
        assert remove_response.status_code == 200
        assert email not in reset_activities[activity_name]["participants"]
    
    def test_signup_freeing_up_spot_for_others(self, client, reset_activities):
        """Test that removing a participant frees up a spot for others"""
        # Arrange
        activity_name = "Full Activity"
        new_email = "spot_seeker@mergington.edu"
        
        # Act: Try to sign up (should fail - full)
        first_attempt = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert: Failed because full
        assert first_attempt.status_code == 400
        
        # Act: Remove existing participant
        client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": "full@mergington.edu"}
        )
        
        # Act: Try to sign up again
        second_attempt = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert: Now succeeds
        assert second_attempt.status_code == 200
        assert new_email in reset_activities[activity_name]["participants"]
