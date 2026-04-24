import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def sample_activity_data():
    """Provide sample activity data for testing"""
    return {
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
        }
    }


@pytest.fixture
def reset_activities(client, sample_activity_data):
    """Reset activities to sample data before each test"""
    from src.app import activities
    
    # Store original activities
    original = activities.copy()
    
    # Reset to sample data
    activities.clear()
    activities.update(sample_activity_data)
    
    yield
    
    # Restore original after test
    activities.clear()
    activities.update(original)
