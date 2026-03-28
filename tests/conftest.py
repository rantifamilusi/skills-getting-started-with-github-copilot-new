import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Arrange: Define fresh test data
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["michael@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 3,
            "participants": []
        },
        "Full Activity": {
            "description": "An activity that is full",
            "schedule": "Mondays, 2:00 PM - 3:00 PM",
            "max_participants": 1,
            "participants": ["full@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(initial_activities)
    
    yield activities
    
    # Cleanup after test
    activities.clear()
