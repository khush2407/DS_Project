import pytest
from fastapi.testclient import TestClient
from redis import Redis
from app import app
import fakeredis.aioredis
import asyncio

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_redis():
    server = fakeredis.aioredis.FakeRedis()
    return server

@pytest.fixture
def test_user_id():
    return "test_user_123"

@pytest.fixture
def test_session_id():
    return "test_session_456"

@pytest.fixture
def test_activity_id():
    return "test_activity_789"

@pytest.fixture
def sample_emotion_data():
    return {
        "emotions": {
            "joy": 0.8,
            "sadness": 0.1,
            "anger": 0.05,
            "fear": 0.05
        },
        "primary_emotion": "joy",
        "summary": "Feeling joyful and positive"
    }

@pytest.fixture
def sample_activity():
    return {
        "id": "test_activity_789",
        "title": "Mindful Breathing",
        "description": "A simple breathing exercise to reduce stress",
        "duration": "5 minutes",
        "difficulty": "beginner",
        "benefits": ["Reduces stress", "Improves focus"],
        "steps": ["Find a quiet place", "Sit comfortably", "Breathe deeply"],
        "emotional_context": "calm"
    } 