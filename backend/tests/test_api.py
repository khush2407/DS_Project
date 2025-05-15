import pytest
from fastapi.testclient import TestClient
from app import app
import json

client = TestClient(app)

def test_root_endpoint(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "endpoints" in data

def test_health_check(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data

def test_analyze_emotion(test_client, sample_emotion_data):
    response = test_client.post(
        "/analyze",
        json={"text": "I am feeling happy and excited today!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "emotions" in data
    assert "primary_emotion" in data
    assert "summary" in data

def test_analyze_emotion_empty_text():
    response = client.post(
        "/analyze",
        json={"text": ""}
    )
    assert response.status_code == 200
    data = response.json()
    assert "emotions" in data
    assert len(data["emotions"]) == 0

def test_get_recommendations(test_client, sample_emotion_data):
    response = test_client.post(
        "/recommend",
        json=sample_emotion_data
    )
    assert response.status_code == 200
    data = response.json()
    assert "activities" in data
    assert "explanation" in data
    assert len(data["activities"]) > 0

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

def test_invalid_analyze_input():
    response = client.post(
        "/analyze",
        json={"invalid": "input"}
    )
    assert response.status_code == 422

def test_invalid_recommendation_input():
    response = client.post(
        "/recommend",
        json={"invalid": "input"}
    )
    assert response.status_code == 422

@pytest.mark.parametrize("text,expected_emotions", [
    ("I am so happy today!", ["joy", "excitement"]),
    ("I feel sad and disappointed", ["sadness", "disappointment"]),
    ("I am angry and frustrated", ["anger", "annoyance"]),
])
def test_emotion_detection_accuracy(text, expected_emotions):
    response = client.post(
        "/analyze",
        json={"text": text}
    )
    assert response.status_code == 200
    data = response.json()
    detected_emotions = [e for e, s in data["emotions"].items() if s > 0.1]
    assert any(emotion in detected_emotions for emotion in expected_emotions)

def test_recommendation_relevance():
    # Test with sadness
    analyze_response = client.post(
        "/analyze",
        json={"text": "I am feeling sad and lonely today"}
    )
    emotion_data = analyze_response.json()
    
    recommend_response = client.post(
        "/recommend",
        json=emotion_data
    )
    data = recommend_response.json()
    
    # Check if recommendations are relevant to sadness
    relevant_activities = ["self_compassion_meditation", "emotional_release"]
    assert any(
        activity["title"].lower() in [a.lower() for a in relevant_activities]
        for activity in data["activities"]
    )

def test_session_management(test_client, test_user_id, test_session_id):
    # Create session
    response = test_client.post(f"/session/create?user_id={test_user_id}")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "user_id" in data
    
    # Get session
    response = test_client.get(f"/session/{test_session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == test_session_id
    
    # Update preferences
    preferences = {
        "difficulty_level": "intermediate",
        "preferred_duration": "medium",
        "favorite_activities": ["activity1"]
    }
    response = test_client.post(
        f"/session/{test_session_id}/preferences",
        json=preferences
    )
    assert response.status_code == 200
    
    # Get preferences
    response = test_client.get(f"/session/{test_session_id}/preferences")
    assert response.status_code == 200
    data = response.json()
    assert "preferred_activities" in data
    assert "total_activities" in data

def test_activity_management(test_client, test_session_id, test_activity_id):
    # Toggle favorite
    response = test_client.post(f"/api/activities/{test_activity_id}/favorite?session_id={test_session_id}")
    assert response.status_code == 200
    data = response.json()
    assert "is_favorite" in data
    
    # Get favorites
    response = test_client.get(f"/api/activities/favorites?session_id={test_session_id}")
    assert response.status_code == 200
    data = response.json()
    assert "favorites" in data
    
    # Update progress
    progress_data = {
        "progress": 0.5,
        "completed_steps": [1, 2],
        "time_spent": 300
    }
    response = test_client.post(
        f"/api/activities/{test_activity_id}/progress?session_id={test_session_id}",
        json=progress_data
    )
    assert response.status_code == 200
    
    # Get progress
    response = test_client.get(f"/api/activities/{test_activity_id}/progress?session_id={test_session_id}")
    assert response.status_code == 200
    data = response.json()
    assert "progress" in data
    assert "completed_steps" in data
    
    # Complete activity
    completion_data = {
        "duration": 600,
        "completed_steps": [1, 2, 3]
    }
    response = test_client.post(
        f"/api/activities/{test_activity_id}/complete?session_id={test_session_id}",
        json=completion_data
    )
    assert response.status_code == 200
    
    # Get history
    response = test_client.get(f"/api/activities/history?session_id={test_session_id}")
    assert response.status_code == 200
    data = response.json()
    assert "history" in data

def test_activity_sharing(test_client, test_session_id, test_activity_id):
    share_data = {
        "activity_id": test_activity_id,
        "platform": "whatsapp",
        "message": "Check out this activity!"
    }
    response = test_client.post(
        f"/api/activities/{test_activity_id}/share?session_id={test_session_id}",
        json=share_data
    )
    assert response.status_code == 200
    data = response.json()
    assert "url" in data

def test_recommendations(test_client, test_session_id):
    response = test_client.get(f"/api/activities/recommendations?session_id={test_session_id}")
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0

def test_error_handling(test_client):
    # Test invalid session
    response = test_client.get("/session/invalid_session")
    assert response.status_code == 404
    
    # Test invalid activity
    response = test_client.get("/api/activities/invalid_activity/progress?session_id=test")
    assert response.status_code == 200  # Returns default progress
    
    # Test invalid share platform
    response = test_client.post(
        "/api/activities/test/share?session_id=test",
        json={"platform": "invalid", "activity_id": "test"}
    )
    assert response.status_code == 400 