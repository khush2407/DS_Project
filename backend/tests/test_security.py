import pytest
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app import app
from services.user_service import UserService

@pytest.fixture
def test_token():
    return jwt.encode(
        {
            "sub": "test_user_123",
            "exp": datetime.utcnow() + timedelta(hours=1)
        },
        "test_secret",
        algorithm="HS256"
    )

def test_authentication_required(test_client):
    # Test endpoints that require authentication
    protected_endpoints = [
        "/api/activities/favorites",
        "/api/activities/history",
        "/session/create",
        "/session/test/preferences"
    ]
    
    for endpoint in protected_endpoints:
        response = test_client.get(endpoint)
        assert response.status_code == 401

def test_token_validation(test_client, test_token):
    # Test with valid token
    headers = {"Authorization": f"Bearer {test_token}"}
    response = test_client.get("/api/activities/favorites", headers=headers)
    assert response.status_code == 200
    
    # Test with invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = test_client.get("/api/activities/favorites", headers=headers)
    assert response.status_code == 401
    
    # Test with expired token
    expired_token = jwt.encode(
        {
            "sub": "test_user_123",
            "exp": datetime.utcnow() - timedelta(hours=1)
        },
        "test_secret",
        algorithm="HS256"
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = test_client.get("/api/activities/favorites", headers=headers)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_user_data_isolation(test_client, test_token, mock_redis):
    headers = {"Authorization": f"Bearer {test_token}"}
    user_service = UserService(mock_redis)
    
    # Create data for user1
    user1_id = "user1"
    await user_service.update_user_preferences(
        user1_id,
        {
            "preferred_activities": ["meditation"],
            "preferred_duration": "short",
            "preferred_difficulty": "beginner"
        }
    )
    
    # Try to access user1's data as user2
    user2_token = jwt.encode(
        {
            "sub": "user2",
            "exp": datetime.utcnow() + timedelta(hours=1)
        },
        "test_secret",
        algorithm="HS256"
    )
    headers2 = {"Authorization": f"Bearer {user2_token}"}
    
    response = test_client.get(f"/api/activities/{user1_id}/progress", headers=headers2)
    assert response.status_code == 403

def test_input_validation(test_client, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # Test SQL injection attempt
    response = test_client.post(
        "/analyze",
        json={"text": "'; DROP TABLE users; --"}
    )
    assert response.status_code == 200  # Should handle safely
    
    # Test XSS attempt
    response = test_client.post(
        "/analyze",
        json={"text": "<script>alert('xss')</script>"}
    )
    assert response.status_code == 200  # Should handle safely
    
    # Test path traversal attempt
    response = test_client.get(
        "/api/activities/../../../etc/passwd/progress",
        headers=headers
    )
    assert response.status_code == 404

def test_rate_limiting(test_client):
    # Test rapid requests to the same endpoint
    for _ in range(100):
        response = test_client.post(
            "/analyze",
            json={"text": "I am happy"}
        )
    
    # Should be rate limited after certain number of requests
    response = test_client.post(
        "/analyze",
        json={"text": "I am happy"}
    )
    assert response.status_code == 429  # Too Many Requests

@pytest.mark.asyncio
async def test_data_encryption(test_client, test_token, mock_redis):
    headers = {"Authorization": f"Bearer {test_token}"}
    user_service = UserService(mock_redis)
    
    # Test sensitive data storage
    sensitive_data = {
        "preferred_activities": ["meditation"],
        "preferred_duration": "short",
        "preferred_difficulty": "beginner",
        "sensitive_info": "secret_data"
    }
    
    await user_service.update_user_preferences("test_user_123", sensitive_data)
    
    # Verify data is not stored in plain text
    stored_data = await user_service.get_user_preferences("test_user_123")
    assert stored_data.get("sensitive_info") != "secret_data"

def test_session_security(test_client, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    
    # Test session creation
    response = test_client.post("/session/create", headers=headers)
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    
    # Test session hijacking attempt
    response = test_client.get(
        f"/session/{session_id}",
        headers={"Authorization": "Bearer different_token"}
    )
    assert response.status_code == 403
    
    # Test session expiration
    expired_token = jwt.encode(
        {
            "sub": "test_user_123",
            "exp": datetime.utcnow() - timedelta(hours=1)
        },
        "test_secret",
        algorithm="HS256"
    )
    response = test_client.get(
        f"/session/{session_id}",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401 