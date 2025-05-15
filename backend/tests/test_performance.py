import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from services.emotion_service import EmotionService
from services.recommendation_service import RecommendationService
from services.user_service import UserService

def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    return wrapper

@pytest.mark.asyncio
async def test_emotion_analysis_performance():
    emotion_service = EmotionService()
    
    # Test with different text lengths
    test_texts = [
        "I am happy",  # Short
        "I am feeling really happy and excited about my new project! The future looks bright.",  # Medium
        "I am feeling really happy and excited about my new project! The future looks bright. " * 10  # Long
    ]
    
    for text in test_texts:
        start_time = time.time()
        emotions, _ = emotion_service.detect_emotions(text)
        end_time = time.time()
        
        # Assert reasonable response time (adjust threshold as needed)
        assert end_time - start_time < 1.0  # Should complete within 1 second
        assert isinstance(emotions, dict)
        assert len(emotions) > 0

@pytest.mark.asyncio
async def test_recommendation_performance(mock_redis, test_user_id):
    user_service = UserService(mock_redis)
    recommendation_service = RecommendationService()
    
    # Test with different numbers of activities
    activity_counts = [5, 10, 20]
    
    for count in activity_counts:
        start_time = time.time()
        recommendations = await user_service.generate_recommendations(
            test_user_id,
            recommendation_service.get_all_activities(),
            limit=count
        )
        end_time = time.time()
        
        # Assert reasonable response time
        assert end_time - start_time < 0.5  # Should complete within 0.5 seconds
        assert len(recommendations) == count

@pytest.mark.asyncio
async def test_concurrent_requests(mock_redis, test_user_id):
    user_service = UserService(mock_redis)
    
    # Test concurrent activity progress updates
    async def update_progress(activity_id, progress):
        return await user_service.update_activity_progress(
            test_user_id,
            activity_id,
            progress,
            [1],
            100
        )
    
    # Create multiple concurrent updates
    tasks = [
        update_progress(f"activity_{i}", i/10)
        for i in range(10)
    ]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    # Assert all updates completed successfully
    assert len(results) == 10
    assert all(isinstance(r, dict) for r in results)
    assert end_time - start_time < 2.0  # Should complete within 2 seconds

@pytest.mark.asyncio
async def test_redis_performance(mock_redis, test_user_id):
    user_service = UserService(mock_redis)
    
    # Test Redis operations performance
    operations = 100
    start_time = time.time()
    
    for i in range(operations):
        await user_service.update_activity_progress(
            test_user_id,
            f"activity_{i}",
            0.5,
            [1, 2],
            300
        )
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Assert reasonable average operation time
    assert total_time / operations < 0.01  # Each operation should take less than 10ms

@pytest.mark.asyncio
async def test_memory_usage(mock_redis, test_user_id):
    user_service = UserService(mock_redis)
    
    # Test memory usage with large activity history
    large_history = []
    for i in range(1000):
        large_history.append({
            "activity_id": f"activity_{i}",
            "completed_at": "2024-01-01T00:00:00",
            "duration": 300,
            "completed_steps": [1, 2, 3]
        })
    
    start_time = time.time()
    for entry in large_history:
        await user_service.add_to_activity_history(
            test_user_id,
            entry["activity_id"],
            entry["duration"],
            entry["completed_steps"]
        )
    end_time = time.time()
    
    # Assert reasonable performance with large dataset
    assert end_time - start_time < 5.0  # Should complete within 5 seconds
    
    # Verify data integrity
    history = await user_service.get_activity_history(test_user_id)
    assert len(history) == 50  # Should maintain limit of 50 entries 