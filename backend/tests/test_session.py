import pytest
from fastapi.testclient import TestClient
from app import app
import json
from datetime import datetime, timedelta

client = TestClient(app)

def test_create_session():
    """Test creating a new session."""
    response = client.post("/session/create?user_id=test_user")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["user_id"] == "test_user"
    assert "created_at" in data
    assert "last_active" in data
    assert "preferences" in data

def test_get_session():
    """Test retrieving a session."""
    # First create a session
    create_response = client.post("/session/create?user_id=test_user")
    session_id = create_response.json()["session_id"]
    
    # Then get the session
    response = client.get(f"/session/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["user_id"] == "test_user"

def test_get_nonexistent_session():
    """Test retrieving a non-existent session."""
    response = client.get("/session/nonexistent")
    assert response.status_code == 404

def test_update_preferences():
    """Test updating user preferences."""
    # First create a session
    create_response = client.post("/session/create?user_id=test_user")
    session_id = create_response.json()["session_id"]
    
    # Update preferences
    preferences = {
        "difficulty_level": "intermediate",
        "preferred_duration": "medium",
        "favorite_activities": ["meditation", "yoga"]
    }
    response = client.post(f"/session/{session_id}/preferences", json=preferences)
    assert response.status_code == 200
    
    # Verify preferences were updated
    get_response = client.get(f"/session/{session_id}")
    assert get_response.status_code == 200
    assert get_response.json()["preferences"] == preferences

def test_emotion_trends():
    """Test getting emotion trends."""
    # Create session
    create_response = client.post("/session/create?user_id=test_user")
    session_id = create_response.json()["session_id"]
    
    # Add some emotion records
    emotions = {"happy": 0.8, "sad": 0.2}
    text = "I'm feeling happy today"
    client.post("/analyze", json={"text": text}, params={"session_id": session_id})
    
    # Get trends
    response = client.get(f"/session/{session_id}/trends")
    assert response.status_code == 200
    data = response.json()
    assert "trends" in data
    assert "total_records" in data
    assert data["total_records"] > 0

def test_activity_preferences():
    """Test getting activity preferences."""
    # Create session
    create_response = client.post("/session/create?user_id=test_user")
    session_id = create_response.json()["session_id"]
    
    # Add some activity records
    emotion_data = {
        "emotions": {"happy": 0.8, "sad": 0.2},
        "primary_emotion": "happy",
        "summary": "Feeling happy"
    }
    client.post("/recommend", json=emotion_data, params={"session_id": session_id})
    
    # Get preferences
    response = client.get(f"/session/{session_id}/preferences")
    assert response.status_code == 200
    data = response.json()
    assert "preferred_activities" in data
    assert "total_activities" in data
    assert data["total_activities"] > 0

def test_delete_session():
    """Test deleting a session."""
    # Create session
    create_response = client.post("/session/create?user_id=test_user")
    session_id = create_response.json()["session_id"]
    
    # Delete session
    response = client.delete(f"/session/{session_id}")
    assert response.status_code == 200
    
    # Verify session is deleted
    get_response = client.get(f"/session/{session_id}")
    assert get_response.status_code == 404

def test_session_integration():
    """Test full session integration with emotion analysis and recommendations."""
    # Create session
    create_response = client.post("/session/create?user_id=test_user")
    session_id = create_response.json()["session_id"]
    
    # Analyze emotions
    text = "I'm feeling happy and excited today"
    emotion_response = client.post("/analyze", json={"text": text}, params={"session_id": session_id})
    assert emotion_response.status_code == 200
    
    # Get recommendations
    emotion_data = emotion_response.json()
    recommend_response = client.post("/recommend", json=emotion_data, params={"session_id": session_id})
    assert recommend_response.status_code == 200
    
    # Check trends and preferences
    trends_response = client.get(f"/session/{session_id}/trends")
    assert trends_response.status_code == 200
    
    preferences_response = client.get(f"/session/{session_id}/preferences")
    assert preferences_response.status_code == 200 