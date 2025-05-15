import pytest
import redis
from datetime import datetime
from services.user_service import UserService
from services.session_service import SessionService

@pytest.fixture
def redis_client():
    return redis.Redis(host='localhost', port=6379, db=0)

@pytest.fixture
def user_service(redis_client):
    return UserService(redis_client)

@pytest.fixture
def session_service():
    return SessionService()

@pytest.mark.asyncio
async def test_user_preferences_migration(redis_client, user_service):
    """Test migration of user preferences data structure"""
    # Create old format data
    old_data = {
        "preferences": {
            "activities": ["meditation"],
            "duration": "short",
            "difficulty": "beginner"
        }
    }
    redis_client.hset("user:test_user", mapping=old_data)
    
    # Migrate to new format
    await user_service.migrate_user_preferences("test_user")
    
    # Verify new format
    new_data = await user_service.get_user_preferences("test_user")
    assert "preferred_activities" in new_data
    assert "preferred_duration" in new_data
    assert "preferred_difficulty" in new_data
    assert new_data["preferred_activities"] == ["meditation"]

@pytest.mark.asyncio
async def test_activity_history_migration(redis_client, user_service):
    """Test migration of activity history data structure"""
    # Create old format data
    old_history = [
        {
            "activity": "meditation",
            "completed": "2024-01-01",
            "time": 300
        }
    ]
    redis_client.set("history:test_user", str(old_history))
    
    # Migrate to new format
    await user_service.migrate_activity_history("test_user")
    
    # Verify new format
    new_history = await user_service.get_activity_history("test_user")
    assert len(new_history) == 1
    assert "activity_id" in new_history[0]
    assert "completed_at" in new_history[0]
    assert "duration" in new_history[0]

@pytest.mark.asyncio
async def test_session_data_migration(redis_client, session_service):
    """Test migration of session data structure"""
    # Create old format data
    old_session = {
        "user_id": "test_user",
        "created": "2024-01-01",
        "emotions": ["happy", "calm"]
    }
    redis_client.hset("session:test_session", mapping=old_session)
    
    # Migrate to new format
    await session_service.migrate_session_data("test_session")
    
    # Verify new format
    new_session = session_service.get_session("test_session")
    assert "user_id" in new_session
    assert "created_at" in new_session
    assert "emotion_records" in new_session

@pytest.mark.asyncio
async def test_activity_progress_migration(redis_client, user_service):
    """Test migration of activity progress data structure"""
    # Create old format data
    old_progress = {
        "progress": 0.5,
        "steps": [1, 2],
        "time": 300
    }
    redis_client.hset("progress:test_user:activity_1", mapping=old_progress)
    
    # Migrate to new format
    await user_service.migrate_activity_progress("test_user", "activity_1")
    
    # Verify new format
    new_progress = await user_service.get_activity_progress("test_user", "activity_1")
    assert "progress" in new_progress
    assert "completed_steps" in new_progress
    assert "total_time_spent" in new_progress

@pytest.mark.asyncio
async def test_favorites_migration(redis_client, user_service):
    """Test migration of favorites data structure"""
    # Create old format data
    old_favorites = ["activity_1", "activity_2"]
    redis_client.sadd("favorites:test_user", *old_favorites)
    
    # Migrate to new format
    await user_service.migrate_favorites("test_user")
    
    # Verify new format
    new_favorites = await user_service.get_favorites("test_user")
    assert len(new_favorites) == 2
    assert all(isinstance(fav, dict) for fav in new_favorites)
    assert all("activity_id" in fav for fav in new_favorites)

@pytest.mark.asyncio
async def test_emotion_records_migration(redis_client, session_service):
    """Test migration of emotion records data structure"""
    # Create old format data
    old_records = [
        {
            "emotion": "happy",
            "timestamp": "2024-01-01T00:00:00",
            "text": "I am happy"
        }
    ]
    redis_client.set("emotions:test_session", str(old_records))
    
    # Migrate to new format
    await session_service.migrate_emotion_records("test_session")
    
    # Verify new format
    new_records = session_service.get_emotion_records("test_session")
    assert len(new_records) == 1
    assert "emotions" in new_records[0]
    assert "timestamp" in new_records[0]
    assert "text" in new_records[0]

@pytest.mark.asyncio
async def test_recommendation_history_migration(redis_client, user_service):
    """Test migration of recommendation history data structure"""
    # Create old format data
    old_history = [
        {
            "activity": "meditation",
            "timestamp": "2024-01-01T00:00:00",
            "score": 0.8
        }
    ]
    redis_client.set("recommendations:test_user", str(old_history))
    
    # Migrate to new format
    await user_service.migrate_recommendation_history("test_user")
    
    # Verify new format
    new_history = await user_service.get_recommendation_history("test_user")
    assert len(new_history) == 1
    assert "activity_id" in new_history[0]
    assert "recommended_at" in new_history[0]
    assert "relevance_score" in new_history[0]

@pytest.mark.asyncio
async def test_migration_rollback(redis_client, user_service):
    """Test that migration rollback works correctly"""
    # Create old format data
    old_data = {
        "preferences": {
            "activities": ["meditation"],
            "duration": "short",
            "difficulty": "beginner"
        }
    }
    redis_client.hset("user:test_user", mapping=old_data)
    
    # Start migration
    try:
        await user_service.migrate_user_preferences("test_user")
        raise Exception("Migration should fail")
    except Exception:
        # Verify rollback
        data = redis_client.hgetall("user:test_user")
        assert data == old_data

@pytest.mark.asyncio
async def test_migration_idempotency(redis_client, user_service):
    """Test that migrations are idempotent"""
    # Create new format data
    new_data = {
        "preferred_activities": ["meditation"],
        "preferred_duration": "short",
        "preferred_difficulty": "beginner"
    }
    redis_client.hset("user:test_user", mapping=new_data)
    
    # Run migration again
    await user_service.migrate_user_preferences("test_user")
    
    # Verify data is unchanged
    data = await user_service.get_user_preferences("test_user")
    assert data == new_data 