import pytest
import asyncio
from datetime import datetime
from services.emotion_service import EmotionService
from services.recommendation_service import RecommendationService
from services.user_service import UserService
from services.session_service import SessionService

@pytest.mark.asyncio
async def test_emotion_to_recommendation_flow(mock_redis):
    # Initialize services
    emotion_service = EmotionService()
    recommendation_service = RecommendationService()
    user_service = UserService(mock_redis)
    
    # Test text
    test_text = "I am feeling anxious and stressed about my upcoming presentation"
    
    # Analyze emotions
    emotions, primary_emotion = emotion_service.detect_emotions(test_text)
    assert primary_emotion in ["anxiety", "fear", "stress"]
    assert any(score > 0.5 for score in emotions.values())
    
    # Get recommendations based on emotions
    recommendations = recommendation_service.get_recommendations(
        emotions,
        primary_emotion,
        None
    )
    
    # Verify recommendations are relevant
    assert len(recommendations) > 0
    assert any(
        "stress" in activity["emotional_context"].lower() or
        "anxiety" in activity["emotional_context"].lower()
        for activity in recommendations
    )

@pytest.mark.asyncio
async def test_user_preferences_affect_recommendations(mock_redis, test_user_id):
    user_service = UserService(mock_redis)
    recommendation_service = RecommendationService()
    
    # Set user preferences
    preferences = {
        "preferred_activities": ["meditation", "breathing"],
        "preferred_duration": "short",
        "preferred_difficulty": "beginner"
    }
    await user_service.update_user_preferences(test_user_id, preferences)
    
    # Get recommendations
    recommendations = await user_service.generate_recommendations(
        test_user_id,
        recommendation_service.get_all_activities(),
        limit=5
    )
    
    # Verify recommendations match preferences
    for activity in recommendations:
        assert activity["difficulty"] == "beginner"
        assert activity["duration"] == "short"
        assert any(
            pref in activity["title"].lower() or
            pref in activity["description"].lower()
            for pref in preferences["preferred_activities"]
        )

@pytest.mark.asyncio
async def test_activity_completion_flow(mock_redis, test_user_id, test_activity_id):
    user_service = UserService(mock_redis)
    session_service = SessionService()
    
    # Start activity
    progress = await user_service.update_activity_progress(
        test_user_id,
        test_activity_id,
        0.25,
        [1],
        150
    )
    assert progress.progress == 0.25
    
    # Update progress
    progress = await user_service.update_activity_progress(
        test_user_id,
        test_activity_id,
        0.75,
        [1, 2, 3],
        450
    )
    assert progress.progress == 0.75
    
    # Complete activity
    await user_service.add_to_activity_history(
        test_user_id,
        test_activity_id,
        600,
        [1, 2, 3, 4]
    )
    
    # Verify history
    history = await user_service.get_activity_history(test_user_id)
    assert len(history) == 1
    assert history[0]["activity_id"] == test_activity_id
    assert history[0]["duration"] == 600
    assert len(history[0]["completed_steps"]) == 4

@pytest.mark.asyncio
async def test_session_persistence(mock_redis, test_user_id):
    session_service = SessionService()
    user_service = UserService(mock_redis)
    
    # Create session
    session_id = session_service.create_session(test_user_id)
    assert session_id is not None
    
    # Add some activity data
    await user_service.add_to_activity_history(
        test_user_id,
        "activity1",
        300,
        [1, 2]
    )
    
    # Get session data
    session_data = session_service.get_session(session_id)
    assert session_data["user_id"] == test_user_id
    
    # Verify activity history is preserved
    history = await user_service.get_activity_history(test_user_id)
    assert len(history) == 1
    assert history[0]["activity_id"] == "activity1"

@pytest.mark.asyncio
async def test_emotion_trends_analysis(mock_redis, test_user_id):
    emotion_service = EmotionService()
    session_service = SessionService()
    
    # Create session
    session_id = session_service.create_session(test_user_id)
    
    # Add multiple emotion records
    test_texts = [
        "I am feeling happy and excited",
        "I feel a bit anxious today",
        "I'm feeling calm and peaceful",
        "I'm really stressed about work"
    ]
    
    for text in test_texts:
        emotions, _ = emotion_service.detect_emotions(text)
        session_service.add_emotion_record(session_id, emotions, text)
    
    # Get emotion trends
    trends = session_service.get_emotion_trends(session_id)
    assert len(trends) > 0
    
    # Verify trend calculations
    assert all(0 <= score <= 1 for score in trends.values())
    assert sum(trends.values()) > 0 