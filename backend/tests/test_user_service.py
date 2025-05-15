import pytest
from datetime import datetime
from services.user_service import UserService, UserPreferences, ActivityProgress

@pytest.mark.asyncio
async def test_get_user_preferences(mock_redis, test_user_id):
    service = UserService(mock_redis)
    preferences = await service.get_user_preferences(test_user_id)
    
    assert isinstance(preferences, UserPreferences)
    assert preferences.preferred_activities == []
    assert preferences.preferred_duration == "medium"
    assert preferences.preferred_difficulty == "beginner"
    assert preferences.favorite_activities == []

@pytest.mark.asyncio
async def test_update_user_preferences(mock_redis, test_user_id):
    service = UserService(mock_redis)
    new_preferences = UserPreferences(
        preferred_activities=["meditation", "yoga"],
        preferred_duration="long",
        preferred_difficulty="intermediate",
        favorite_activities=["activity1", "activity2"]
    )
    
    updated = await service.update_user_preferences(test_user_id, new_preferences)
    assert updated == new_preferences
    
    retrieved = await service.get_user_preferences(test_user_id)
    assert retrieved == new_preferences

@pytest.mark.asyncio
async def test_toggle_favorite(mock_redis, test_user_id, test_activity_id):
    service = UserService(mock_redis)
    
    # Test adding to favorites
    is_favorite = await service.toggle_favorite(test_user_id, test_activity_id)
    assert is_favorite is True
    
    favorites = await service.get_favorites(test_user_id)
    assert test_activity_id in favorites
    
    # Test removing from favorites
    is_favorite = await service.toggle_favorite(test_user_id, test_activity_id)
    assert is_favorite is False
    
    favorites = await service.get_favorites(test_user_id)
    assert test_activity_id not in favorites

@pytest.mark.asyncio
async def test_activity_progress(mock_redis, test_user_id, test_activity_id):
    service = UserService(mock_redis)
    
    # Test updating progress
    progress = await service.update_activity_progress(
        test_user_id,
        test_activity_id,
        0.5,
        [1, 2],
        300
    )
    
    assert isinstance(progress, ActivityProgress)
    assert progress.progress == 0.5
    assert progress.completed_steps == [1, 2]
    assert progress.total_time_spent == 300
    
    # Test retrieving progress
    retrieved = await service.get_activity_progress(test_user_id, test_activity_id)
    assert retrieved == progress

@pytest.mark.asyncio
async def test_activity_history(mock_redis, test_user_id, test_activity_id):
    service = UserService(mock_redis)
    
    # Test adding to history
    await service.add_to_activity_history(
        test_user_id,
        test_activity_id,
        600,
        [1, 2, 3]
    )
    
    # Test retrieving history
    history = await service.get_activity_history(test_user_id)
    assert len(history) == 1
    assert history[0]["activity_id"] == test_activity_id
    assert history[0]["duration"] == 600
    assert history[0]["completed_steps"] == [1, 2, 3]

@pytest.mark.asyncio
async def test_generate_recommendations(mock_redis, test_user_id):
    service = UserService(mock_redis)
    
    # Set up user preferences
    preferences = UserPreferences(
        preferred_activities=["meditation"],
        preferred_duration="medium",
        preferred_difficulty="beginner",
        favorite_activities=["activity1"]
    )
    await service.update_user_preferences(test_user_id, preferences)
    
    # Add some activity history
    await service.add_to_activity_history(
        test_user_id,
        "activity2",
        300,
        [1, 2]
    )
    
    # Test recommendations
    available_activities = [
        {
            "id": "activity1",
            "title": "Meditation",
            "difficulty": "beginner",
            "duration": "medium",
            "categories": ["meditation"]
        },
        {
            "id": "activity2",
            "title": "Yoga",
            "difficulty": "intermediate",
            "duration": "long",
            "categories": ["exercise"]
        }
    ]
    
    recommendations = await service.generate_recommendations(
        test_user_id,
        available_activities,
        limit=2
    )
    
    assert len(recommendations) == 2
    assert recommendations[0]["id"] == "activity1"  # Should be first due to being favorite 