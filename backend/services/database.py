from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING
from typing import Optional, Dict, List, Any
import logging
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import certifi
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from .schemas import (
    UserPreferences, ActivityProgress, EmotionAnalysis,
    ActivityHistory, Session, FavoriteActivity
)

load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Base exception for database errors"""
    pass

class ConnectionError(DatabaseError):
    """Raised when database connection fails"""
    pass

class ValidationError(DatabaseError):
    """Raised when data validation fails"""
    pass

class Database:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.in_memory_mode = False
        self.in_memory_db = {
            "users": {},
            "sessions": {},
            "activity_history": {},
            "emotion_analysis": {},
            "favorites": {},
            "activity_progress": {}
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def connect(self):
        """Connect to MongoDB Atlas with retry logic or use in-memory mode"""
        try:
            mongo_uri = os.getenv("MONGODB_URI")
            if not mongo_uri:
                raise ValueError("MONGODB_URI environment variable is not set")

            try:
                self.client = AsyncIOMotorClient(
                    mongo_uri,
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=5000,
                    retryWrites=True,
                    w="majority"
                )
                
                await self.client.admin.command('ping')
                
                db_name = os.getenv("MONGODB_DATABASE", "wellness_app")
                self.db = self.client[db_name]
                
                logger.info("Successfully connected to MongoDB Atlas")
                await self._create_indexes()
                self.in_memory_mode = False
                
            except Exception as e:
                logger.warning(f"MongoDB connection failed: {e}. Using in-memory storage instead.")
                self.in_memory_mode = True
                self.client = None
                self.db = None
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise ConnectionError(f"Database initialization failed: {str(e)}")

    async def _create_indexes(self):
        """Create comprehensive indexes for all collections"""
        try:
            # User indexes
            user_indexes = [
                IndexModel([("email", ASCENDING)], unique=True),
                IndexModel([("username", ASCENDING)], unique=True),
                IndexModel([("created_at", DESCENDING)])
            ]
            await self.db.users.create_indexes(user_indexes)
            
            # Session indexes
            session_indexes = [
                IndexModel([("created_at", DESCENDING)], expireAfterSeconds=86400),
                IndexModel([("user_id", ASCENDING)]),
                IndexModel([("last_active", DESCENDING)])
            ]
            await self.db.sessions.create_indexes(session_indexes)

            # Activity history indexes
            activity_history_indexes = [
                IndexModel([
                    ("session_id", ASCENDING),
                    ("timestamp", DESCENDING)
                ]),
                IndexModel([("activity_id", ASCENDING)]),
                IndexModel([("completed", ASCENDING)]),
                IndexModel([("duration", DESCENDING)])
            ]
            await self.db.activity_history.create_indexes(activity_history_indexes)

            # Emotion analysis indexes
            emotion_analysis_indexes = [
                IndexModel([
                    ("session_id", ASCENDING),
                    ("timestamp", DESCENDING)
                ]),
                IndexModel([("primary_emotion", ASCENDING)]),
                IndexModel([("confidence", DESCENDING)])
            ]
            await self.db.emotion_analysis.create_indexes(emotion_analysis_indexes)

            # Favorites indexes
            favorites_indexes = [
                IndexModel([
                    ("session_id", ASCENDING),
                    ("activity_id", ASCENDING)
                ], unique=True),
                IndexModel([("added_at", DESCENDING)]),
                IndexModel([("category", ASCENDING)])
            ]
            await self.db.favorites.create_indexes(favorites_indexes)

            # Activity progress indexes
            progress_indexes = [
                IndexModel([
                    ("session_id", ASCENDING),
                    ("activity_id", ASCENDING)
                ], unique=True),
                IndexModel([("last_updated", DESCENDING)])
            ]
            await self.db.activity_progress.create_indexes(progress_indexes)

            logger.info("Successfully created all database indexes")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise DatabaseError(f"Index creation failed: {str(e)}")

    async def backup_database(self):
        """Create a backup of the database"""
        try:
            backup_dir = os.path.join(os.getcwd(), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
            
            # Create backup using mongodump
            os.system(f"mongodump --uri='{os.getenv('MONGODB_URI')}' --out={backup_path}")
            
            logger.info(f"Database backup created at {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise DatabaseError(f"Backup failed: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_session(self, session_data: Dict[str, Any]) -> str:
        """Create a new session with validation"""
        try:
            session = Session(**session_data)
            session_dict = session.dict()
            
            if self.in_memory_mode:
                # Generate a simple ID for in-memory mode
                import uuid
                session_id = str(uuid.uuid4())
                self.in_memory_db["sessions"][session_id] = session_dict
                return session_id
            else:
                result = await self.db.sessions.insert_one(session_dict)
                return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise ValidationError(f"Session creation failed: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def save_activity_progress(self, session_id: str, activity_id: str, progress: Dict[str, Any]) -> bool:
        """Save activity progress with validation"""
        try:
            progress_data = ActivityProgress(**progress)
            progress_dict = progress_data.dict()
            
            if self.in_memory_mode:
                key = f"{session_id}_{activity_id}"
                self.in_memory_db["activity_progress"][key] = progress_dict
                return True
            else:
                result = await self.db.activity_progress.update_one(
                    {"session_id": session_id, "activity_id": activity_id},
                    {"$set": progress_dict},
                    upsert=True
                )
                return True
        except Exception as e:
            logger.error(f"Failed to save activity progress: {e}")
            raise ValidationError(f"Progress save failed: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def save_emotion_analysis(self, session_id: str, emotion_data: Dict[str, Any]) -> str:
        """Save emotion analysis with validation"""
        try:
            analysis = EmotionAnalysis(**emotion_data)
            analysis_dict = analysis.dict()
            
            if self.in_memory_mode:
                import uuid
                analysis_id = str(uuid.uuid4())
                analysis_dict["_id"] = analysis_id
                
                if session_id not in self.in_memory_db["emotion_analysis"]:
                    self.in_memory_db["emotion_analysis"][session_id] = []
                
                self.in_memory_db["emotion_analysis"][session_id].append(analysis_dict)
                return analysis_id
            else:
                result = await self.db.emotion_analysis.insert_one(analysis_dict)
                return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to save emotion analysis: {e}")
            raise ValidationError(f"Emotion analysis save failed: {str(e)}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def save_activity_history(self, session_id: str, activity_data: Dict[str, Any]) -> str:
        """Save activity to history with validation"""
        try:
            activity_data["session_id"] = session_id
            history = ActivityHistory(**activity_data)
            history_dict = history.dict()
            
            if self.in_memory_mode:
                import uuid
                activity_id = str(uuid.uuid4())
                history_dict["_id"] = activity_id
                
                if session_id not in self.in_memory_db["activity_history"]:
                    self.in_memory_db["activity_history"][session_id] = []
                
                self.in_memory_db["activity_history"][session_id].append(history_dict)
                return activity_id
            else:
                result = await self.db.activity_history.insert_one(history_dict)
                return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to save activity history: {e}")
            raise ValidationError(f"Activity history save failed: {str(e)}")

    async def get_activity_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get activity history with pagination"""
        try:
            if self.in_memory_mode:
                if session_id not in self.in_memory_db["activity_history"]:
                    return []
                
                # Sort by timestamp in descending order
                sorted_history = sorted(
                    self.in_memory_db["activity_history"][session_id],
                    key=lambda x: x.get("timestamp", 0),
                    reverse=True
                )
                
                # Apply limit
                return sorted_history[:limit]
            else:
                cursor = self.db.activity_history.find(
                    {"session_id": session_id}
                ).sort("timestamp", -1).limit(limit)
                return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Failed to get activity history: {e}")
            raise DatabaseError(f"Failed to get activity history: {str(e)}")

    async def get_activity_stats(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive activity statistics"""
        try:
            pipeline = [
                {"$match": {"session_id": session_id}},
                {"$group": {
                    "_id": None,
                    "total_activities": {"$sum": 1},
                    "completed_activities": {
                        "$sum": {"$cond": ["$completed", 1, 0]}
                    },
                    "total_duration": {"$sum": "$duration"},
                    "avg_duration": {"$avg": "$duration"},
                    "categories": {"$addToSet": "$category"}
                }},
                {"$project": {
                    "_id": 0,
                    "total_activities": 1,
                    "completed_activities": 1,
                    "total_duration": 1,
                    "avg_duration": 1,
                    "category_count": {"$size": "$categories"}
                }}
            ]
            
            result = await self.db.activity_history.aggregate(pipeline).to_list(length=1)
            return result[0] if result else {
                "total_activities": 0,
                "completed_activities": 0,
                "total_duration": 0,
                "avg_duration": 0,
                "category_count": 0
            }
        except Exception as e:
            logger.error(f"Failed to get activity stats: {e}")
            raise DatabaseError(f"Failed to get activity stats: {str(e)}")

    async def get_emotion_trends(self, session_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get emotion analysis trends with aggregation"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            pipeline = [
                {"$match": {
                    "session_id": session_id,
                    "timestamp": {"$gte": start_date}
                }},
                {"$group": {
                    "_id": {
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                        "emotion": "$primary_emotion"
                    },
                    "count": {"$sum": 1},
                    "avg_confidence": {"$avg": "$confidence"}
                }},
                {"$sort": {"_id.date": 1, "count": -1}}
            ]
            
            return await self.db.emotion_analysis.aggregate(pipeline).to_list(length=None)
        except Exception as e:
            logger.error(f"Failed to get emotion trends: {e}")
            raise DatabaseError(f"Failed to get emotion trends: {str(e)}")

    async def cleanup_old_data(self, days: int = 90):
        """Clean up old data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Delete old sessions
            await self.db.sessions.delete_many({
                "last_active": {"$lt": cutoff_date}
            })
            
            # Delete old activity history
            await self.db.activity_history.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            # Delete old emotion analysis
            await self.db.emotion_analysis.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            logger.info(f"Cleaned up data older than {days} days")
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            raise DatabaseError(f"Cleanup failed: {str(e)}")
            
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user with validation"""
        try:
            from .schemas import User
            user = User(**user_data)
            user_dict = user.dict()
            
            if self.in_memory_mode:
                import uuid
                user_id = str(uuid.uuid4())
                user_dict["_id"] = user_id
                
                # Store by both ID and email for easy lookup
                self.in_memory_db["users"][user_id] = user_dict
                self.in_memory_db["users"][user_dict["email"]] = user_dict
                
                return user_id
            else:
                result = await self.db.users.insert_one(user_dict)
                return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise ValidationError(f"User creation failed: {str(e)}")
            
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            if self.in_memory_mode:
                return self.in_memory_db["users"].get(email)
            else:
                user = await self.db.users.find_one({"email": email})
                return user
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            raise DatabaseError(f"Failed to get user: {str(e)}")
            
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            if self.in_memory_mode:
                return self.in_memory_db["users"].get(user_id)
            else:
                user = await self.db.users.find_one({"id": user_id})
                return user
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            raise DatabaseError(f"Failed to get user: {str(e)}")
            
    async def update_user_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            result = await self.db.users.update_one(
                {"id": user_id},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update user last login: {e}")
            raise DatabaseError(f"Failed to update user: {str(e)}")

# Create a global database instance
db = Database()