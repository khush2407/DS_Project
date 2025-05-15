from typing import List, Dict, Optional
from datetime import datetime
import json
from redis import Redis
from pydantic import BaseModel

class UserPreferences(BaseModel):
    preferred_activities: List[str]
    preferred_duration: str
    preferred_difficulty: str
    favorite_activities: List[str]

class ActivityProgress(BaseModel):
    activity_id: str
    progress: float
    last_accessed: datetime
    total_time_spent: int
    completed_steps: List[int]

class UserService:
    def __init__(self, redis_client: Redis = None):
        self.redis = redis_client
        self.redis_available = redis_client is not None
        self.preferences_key = "user:{}:preferences"
        self.favorites_key = "user:{}:favorites"
        self.progress_key = "user:{}:progress:{}"
        self.activity_history_key = "user:{}:activity_history"
        self.recommendations_key = "user:{}:recommendations"
        
        # In-memory storage if Redis is not available
        if not self.redis_available:
            self.memory_storage = {
                'preferences': {},
                'favorites': {},
                'progress': {},
                'activity_history': {}
            }

    async def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get user preferences from storage."""
        key = self.preferences_key.format(user_id)
        
        if self.redis_available:
            try:
                data = self.redis.get(key)
                if data:
                    return UserPreferences(**json.loads(data))
            except Exception as e:
                print(f"Error getting user preferences from Redis: {str(e)}")
                # Fall back to in-memory storage
                self.redis_available = False
        
        # Use in-memory storage if Redis is not available or failed
        if not self.redis_available:
            if user_id in self.memory_storage['preferences']:
                return UserPreferences(**self.memory_storage['preferences'][user_id])
        
        # Default preferences if not found
        return UserPreferences(
            preferred_activities=[],
            preferred_duration="medium",
            preferred_difficulty="beginner",
            favorite_activities=[]
        )

    async def update_user_preferences(self, user_id: str, preferences: UserPreferences) -> UserPreferences:
        """Update user preferences in storage."""
        key = self.preferences_key.format(user_id)
        
        if self.redis_available:
            try:
                self.redis.set(key, preferences.json())
            except Exception as e:
                print(f"Error updating user preferences in Redis: {str(e)}")
                # Fall back to in-memory storage
                self.redis_available = False
                self.memory_storage['preferences'][user_id] = json.loads(preferences.json())
        else:
            # Use in-memory storage
            self.memory_storage['preferences'][user_id] = json.loads(preferences.json())
            
        return preferences

    async def toggle_favorite(self, user_id: str, activity_id: str) -> bool:
        """Toggle favorite status for an activity."""
        key = self.favorites_key.format(user_id)
        
        if self.redis_available:
            try:
                is_favorite = self.redis.sismember(key, activity_id)
                
                if is_favorite:
                    self.redis.srem(key, activity_id)
                else:
                    self.redis.sadd(key, activity_id)
                    
                return not is_favorite
            except Exception as e:
                print(f"Error toggling favorite in Redis: {str(e)}")
                # Fall back to in-memory storage
                self.redis_available = False
        
        # Use in-memory storage if Redis is not available or failed
        if not self.redis_available:
            if user_id not in self.memory_storage['favorites']:
                self.memory_storage['favorites'][user_id] = set()
                
            favorites = self.memory_storage['favorites'][user_id]
            is_favorite = activity_id in favorites
            
            if is_favorite:
                favorites.remove(activity_id)
            else:
                favorites.add(activity_id)
                
            return not is_favorite

    async def get_favorites(self, user_id: str) -> List[str]:
        """Get list of favorite activities."""
        key = self.favorites_key.format(user_id)
        
        if self.redis_available:
            try:
                return list(self.redis.smembers(key))
            except Exception as e:
                print(f"Error getting favorites from Redis: {str(e)}")
                # Fall back to in-memory storage
                self.redis_available = False
        
        # Use in-memory storage if Redis is not available or failed
        if not self.redis_available:
            if user_id in self.memory_storage['favorites']:
                return list(self.memory_storage['favorites'][user_id])
            return []

    async def update_activity_progress(
        self,
        user_id: str,
        activity_id: str,
        progress: float,
        completed_steps: List[int],
        time_spent: int
    ) -> ActivityProgress:
        """Update activity progress."""
        key = self.progress_key.format(user_id, activity_id)
        activity_progress = ActivityProgress(
            activity_id=activity_id,
            progress=progress,
            last_accessed=datetime.utcnow(),
            total_time_spent=time_spent,
            completed_steps=completed_steps
        )
        
        if self.redis_available:
            try:
                self.redis.set(key, activity_progress.json())
            except Exception as e:
                print(f"Error updating activity progress in Redis: {str(e)}")
                # Fall back to in-memory storage
                self.redis_available = False
                if user_id not in self.memory_storage['progress']:
                    self.memory_storage['progress'][user_id] = {}
                self.memory_storage['progress'][user_id][activity_id] = json.loads(activity_progress.json())
        else:
            # Use in-memory storage
            if user_id not in self.memory_storage['progress']:
                self.memory_storage['progress'][user_id] = {}
            self.memory_storage['progress'][user_id][activity_id] = json.loads(activity_progress.json())
            
        return activity_progress

    async def get_activity_progress(self, user_id: str, activity_id: str) -> Optional[ActivityProgress]:
        """Get activity progress."""
        key = self.progress_key.format(user_id, activity_id)
        
        if self.redis_available:
            try:
                data = self.redis.get(key)
                if data:
                    return ActivityProgress(**json.loads(data))
            except Exception as e:
                print(f"Error getting activity progress from Redis: {str(e)}")
                # Fall back to in-memory storage
                self.redis_available = False
        
        # Use in-memory storage if Redis is not available or failed
        if not self.redis_available:
            if user_id in self.memory_storage['progress'] and activity_id in self.memory_storage['progress'][user_id]:
                return ActivityProgress(**self.memory_storage['progress'][user_id][activity_id])
                
        return None

    async def add_to_activity_history(
        self,
        user_id: str,
        activity_id: str,
        duration: int,
        completed_steps: List[int]
    ) -> None:
        """Add activity to history."""
        key = self.activity_history_key.format(user_id)
        history_entry = {
            "activity_id": activity_id,
            "completed_at": datetime.utcnow().isoformat(),
            "duration": duration,
            "completed_steps": completed_steps
        }
        
        if self.redis_available:
            try:
                self.redis.lpush(key, json.dumps(history_entry))
                self.redis.ltrim(key, 0, 49)  # Keep last 50 activities
            except Exception as e:
                print(f"Error adding to activity history in Redis: {str(e)}")
                # Fall back to in-memory storage
                self.redis_available = False
                if user_id not in self.memory_storage['activity_history']:
                    self.memory_storage['activity_history'][user_id] = []
                self.memory_storage['activity_history'][user_id].insert(0, history_entry)
                # Keep last 50 activities
                if len(self.memory_storage['activity_history'][user_id]) > 50:
                    self.memory_storage['activity_history'][user_id] = self.memory_storage['activity_history'][user_id][:50]
        else:
            # Use in-memory storage
            if user_id not in self.memory_storage['activity_history']:
                self.memory_storage['activity_history'][user_id] = []
            self.memory_storage['activity_history'][user_id].insert(0, history_entry)
            # Keep last 50 activities
            if len(self.memory_storage['activity_history'][user_id]) > 50:
                self.memory_storage['activity_history'][user_id] = self.memory_storage['activity_history'][user_id][:50]

    async def get_activity_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get activity history."""
        key = self.activity_history_key.format(user_id)
        
        if self.redis_available:
            try:
                history = self.redis.lrange(key, 0, limit - 1)
                return [json.loads(entry) for entry in history]
            except Exception as e:
                print(f"Error getting activity history from Redis: {str(e)}")
                # Fall back to in-memory storage
                self.redis_available = False
        
        # Use in-memory storage if Redis is not available or failed
        if not self.redis_available:
            if user_id in self.memory_storage['activity_history']:
                return self.memory_storage['activity_history'][user_id][:limit]
            return []

    async def generate_recommendations(
        self,
        user_id: str,
        available_activities: List[Dict],
        limit: int = 5
    ) -> List[Dict]:
        """Generate personalized activity recommendations."""
        # Get user preferences and history
        preferences = await self.get_user_preferences(user_id)
        history = await self.get_activity_history(user_id)
        favorites = await self.get_favorites(user_id)

        # Score activities based on user preferences and history
        scored_activities = []
        for activity in available_activities:
            score = 0
            
            # Score based on difficulty preference
            if activity["difficulty"] == preferences.preferred_difficulty:
                score += 2
            
            # Score based on duration preference
            if activity["duration"] == preferences.preferred_duration:
                score += 2
            
            # Score based on favorites
            if activity["id"] in favorites:
                score += 3
            
            # Score based on activity history
            activity_completion_count = sum(
                1 for entry in history if entry["activity_id"] == activity["id"]
            )
            score += min(activity_completion_count, 3)  # Cap at 3 points
            
            # Score based on categories
            if any(cat in preferences.preferred_activities for cat in activity.get("categories", [])):
                score += 2
            
            scored_activities.append((activity, score))

        # Sort by score and return top recommendations
        scored_activities.sort(key=lambda x: x[1], reverse=True)
        return [activity for activity, _ in scored_activities[:limit]] 