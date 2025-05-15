import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from services.emotion_service import EmotionService
from services.recommendation_service import RecommendationService
from services.user_service import UserService

@pytest.mark.asyncio
async def test_high_concurrent_users(mock_redis):
    # Simulate 100 concurrent users
    num_users = 100
    user_service = UserService(mock_redis)
    emotion_service = EmotionService()
    
    async def simulate_user(user_id):
        # Create user session
        await user_service.update_user_preferences(
            user_id,
            {
                "preferred_activities": ["meditation"],
                "preferred_duration": "short",
                "preferred_difficulty": "beginner"
            }
        )
        
        # Analyze emotions
        emotions, _ = emotion_service.detect_emotions(
            "I am feeling happy and excited today!"
        )
        
        # Update activity progress
        await user_service.update_activity_progress(
            user_id,
            "activity_1",
            0.5,
            [1, 2],
            300
        )
        
        return True
    
    # Create tasks for all users
    tasks = [simulate_user(f"user_{i}") for i in range(num_users)]
    
    # Execute all tasks concurrently
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    # Verify all operations completed successfully
    assert all(results)
    assert end_time - start_time < 10.0  # Should complete within 10 seconds

@pytest.mark.asyncio
async def test_rapid_emotion_analysis(mock_redis):
    emotion_service = EmotionService()
    
    # Test rapid emotion analysis requests
    num_requests = 50
    test_texts = [
        "I am feeling happy",
        "I am feeling sad",
        "I am feeling angry",
        "I am feeling anxious",
        "I am feeling excited"
    ] * 10  # Repeat to get 50 texts
    
    async def analyze_emotion(text):
        return emotion_service.detect_emotions(text)
    
    # Create tasks for all requests
    tasks = [analyze_emotion(text) for text in test_texts]
    
    # Execute all tasks concurrently
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    # Verify all analyses completed successfully
    assert len(results) == num_requests
    assert all(isinstance(r[0], dict) for r in results)
    assert end_time - start_time < 5.0  # Should complete within 5 seconds

@pytest.mark.asyncio
async def test_activity_recommendation_load(mock_redis):
    user_service = UserService(mock_redis)
    recommendation_service = RecommendationService()
    
    # Test rapid recommendation requests
    num_requests = 30
    user_ids = [f"user_{i}" for i in range(num_requests)]
    
    async def get_recommendations(user_id):
        return await user_service.generate_recommendations(
            user_id,
            recommendation_service.get_all_activities(),
            limit=5
        )
    
    # Create tasks for all requests
    tasks = [get_recommendations(user_id) for user_id in user_ids]
    
    # Execute all tasks concurrently
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    # Verify all recommendations completed successfully
    assert len(results) == num_requests
    assert all(len(r) == 5 for r in results)
    assert end_time - start_time < 5.0  # Should complete within 5 seconds

@pytest.mark.asyncio
async def test_redis_write_load(mock_redis):
    user_service = UserService(mock_redis)
    
    # Test rapid Redis write operations
    num_operations = 200
    operations = []
    
    for i in range(num_operations):
        operations.append({
            "user_id": f"user_{i % 10}",  # 10 different users
            "activity_id": f"activity_{i}",
            "progress": i / num_operations,
            "steps": [1, 2, 3],
            "time": 300
        })
    
    async def perform_operation(op):
        return await user_service.update_activity_progress(
            op["user_id"],
            op["activity_id"],
            op["progress"],
            op["steps"],
            op["time"]
        )
    
    # Create tasks for all operations
    tasks = [perform_operation(op) for op in operations]
    
    # Execute all tasks concurrently
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    # Verify all operations completed successfully
    assert len(results) == num_operations
    assert all(isinstance(r, dict) for r in results)
    assert end_time - start_time < 5.0  # Should complete within 5 seconds

@pytest.mark.asyncio
async def test_mixed_workload(mock_redis):
    # Test mixed workload of different operations
    user_service = UserService(mock_redis)
    emotion_service = EmotionService()
    recommendation_service = RecommendationService()
    
    num_operations = 50
    operations = []
    
    # Create mixed operations
    for i in range(num_operations):
        if i % 3 == 0:
            # Emotion analysis
            operations.append(("emotion", f"I am feeling {'happy' if i % 2 == 0 else 'sad'}"))
        elif i % 3 == 1:
            # Activity progress
            operations.append(("progress", {
                "user_id": f"user_{i % 5}",
                "activity_id": f"activity_{i}",
                "progress": 0.5,
                "steps": [1, 2],
                "time": 300
            }))
        else:
            # Recommendations
            operations.append(("recommend", f"user_{i % 5}"))
    
    async def perform_operation(op_type, data):
        if op_type == "emotion":
            return emotion_service.detect_emotions(data)
        elif op_type == "progress":
            return await user_service.update_activity_progress(
                data["user_id"],
                data["activity_id"],
                data["progress"],
                data["steps"],
                data["time"]
            )
        else:  # recommend
            return await user_service.generate_recommendations(
                data,
                recommendation_service.get_all_activities(),
                limit=3
            )
    
    # Create tasks for all operations
    tasks = [perform_operation(op[0], op[1]) for op in operations]
    
    # Execute all tasks concurrently
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    # Verify all operations completed successfully
    assert len(results) == num_operations
    assert end_time - start_time < 10.0  # Should complete within 10 seconds 