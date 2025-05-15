import asyncio
import logging
from datetime import datetime, timedelta
from services.database import db
from services.schemas import (
    UserPreferences, ActivityProgress, EmotionAnalysis,
    ActivityHistory, Session, FavoriteActivity,
    DifficultyLevel, Duration
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_connection():
    """Test MongoDB connection"""
    try:
        await db.connect()
        logger.info("Successfully connected to MongoDB")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return False

async def insert_sample_data():
    """Insert sample data into MongoDB"""
    try:
        # Create a test session
        session_data = {
            "user_id": "test_user_1",
            "preferences": {
                "difficulty_level": DifficultyLevel.INTERMEDIATE,
                "preferred_duration": Duration.MEDIUM,
                "categories": ["meditation", "breathing", "yoga"],
                "notifications": True
            }
        }
        session_id = await db.create_session(session_data)
        logger.info(f"Created test session with ID: {session_id}")

        # Insert activity progress
        progress_data = {
            "progress": 75.5,
            "completed_steps": [1, 2, 3],
            "time_spent": 1800  # 30 minutes
        }
        await db.save_activity_progress(session_id, "activity_1", progress_data)
        logger.info("Inserted activity progress")

        # Insert emotion analysis
        emotion_data = {
            "emotions": {
                "calm": 0.8,
                "focused": 0.6,
                "relaxed": 0.7
            },
            "primary_emotion": "calm",
            "summary": "Feeling calm and relaxed after meditation",
            "confidence": 0.85,
            "text": "I feel very calm and relaxed after my meditation session"
        }
        await db.save_emotion_analysis(session_id, emotion_data)
        logger.info("Inserted emotion analysis")

        # Insert activity history
        history_data = {
            "activity_id": "activity_1",
            "activity_title": "Morning Meditation",
            "start_time": datetime.utcnow() - timedelta(hours=1),
            "end_time": datetime.utcnow(),
            "duration": 30,
            "completed": True,
            "progress": 100,
            "steps_completed": [1, 2, 3, 4, 5]
        }
        await db.save_activity_history(session_id, history_data)
        logger.info("Inserted activity history")

        # Get and verify the data
        stats = await db.get_activity_stats(session_id)
        logger.info(f"Activity stats: {stats}")

        trends = await db.get_emotion_trends(session_id)
        logger.info(f"Emotion trends: {trends}")

        return True
    except Exception as e:
        logger.error(f"Failed to insert sample data: {e}")
        return False

async def main():
    """Main test function"""
    if await test_connection():
        if await insert_sample_data():
            logger.info("Successfully completed all tests")
        else:
            logger.error("Failed to insert sample data")
    else:
        logger.error("Failed to connect to MongoDB")

if __name__ == "__main__":
    asyncio.run(main()) 