from typing import Dict, List, Optional
import redis
import json
from datetime import datetime, timedelta
import uuid

class SessionService:
    def __init__(self):
        self.session_expiry = timedelta(days=30)  # Sessions expire after 30 days
        self.sessions = {}  # Initialize in-memory storage for sessions
        self.user_sessions = {}  # Initialize in-memory storage for user sessions
        
        # Try to connect to Redis, but don't fail if it's not available
        try:
            self.redis_client = redis.Redis(
                host='redis',
                port=6379,
                db=1,
                decode_responses=True,
                socket_connect_timeout=2,  # Set a short timeout
                socket_timeout=2
            )
            # Test the connection
            self.redis_client.ping()
            self.redis_available = True
            print("Successfully connected to Redis for session management")
        except Exception as e:
            print(f"Redis not available: {str(e)}. Using in-memory session storage instead.")
            self.redis_available = False

    def create_session(self, user_id: str) -> str:
        """Create a new session for a user."""
        session_id = str(uuid.uuid4())
        session_data = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
            "emotion_history": [],
            "activity_history": [],
            "preferences": {
                "difficulty_level": "beginner",
                "preferred_duration": "short",
                "favorite_activities": []
            }
        }
        
        session_key = f"session:{session_id}"
        user_session_key = f"user_sessions:{user_id}"
        
        # Try to store in Redis if available
        if self.redis_available:
            try:
                # Store session data in Redis
                self.redis_client.setex(
                    session_key,
                    int(self.session_expiry.total_seconds()),  # Convert timedelta to seconds
                    json.dumps(session_data)
                )
                
                # Store session ID for user in Redis
                self.redis_client.setex(
                    user_session_key,
                    int(self.session_expiry.total_seconds()),
                    session_id
                )
                print(f"Successfully created session in Redis: {session_id}")
            except Exception as e:
                print(f"Error creating session in Redis: {str(e)}")
                print("Falling back to in-memory storage")
                # Disable Redis for future operations
                self.redis_available = False
                # Continue with in-memory storage
        
        # Always store in memory as a backup or if Redis is not available
        self.sessions[session_key] = session_data
        self.user_sessions[user_session_key] = session_id
        
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data by session ID."""
        session_key = f"session:{session_id}"
        
        # Try Redis first if available
        if self.redis_available:
            try:
                session_data = self.redis_client.get(session_key)
                if session_data:
                    return json.loads(session_data)
            except Exception as e:
                print(f"Error getting session from Redis: {str(e)}")
                print("Falling back to in-memory storage")
                # Disable Redis for future operations
                self.redis_available = False
        
        # Use in-memory storage if Redis is not available or failed
        if session_key in self.sessions:
            return self.sessions[session_key]
        
        # If session not found, create a new one with basic structure
        # This prevents 500 errors when a session ID exists but data is missing
        if session_id:
            print(f"Session {session_id} not found, creating a placeholder session")
            new_session = {
                "user_id": f"user-{session_id}",
                "created_at": datetime.now().isoformat(),
                "last_active": datetime.now().isoformat(),
                "emotion_history": [],
                "activity_history": [],
                "preferences": {
                    "difficulty_level": "beginner",
                    "preferred_duration": "short",
                    "favorite_activities": []
                }
            }
            self.sessions[session_key] = new_session
            return new_session
                
        return None

    def update_session(self, session_id: str, updates: Dict):
        """Update session data."""
        session_data = self.get_session(session_id)
        if session_data:
            # If updates is the entire session data, use it directly
            if isinstance(updates, dict) and "user_id" in updates and "created_at" in updates:
                session_data = updates
            else:
                # Otherwise, update the existing session data
                session_data.update(updates)
            
            # Always update the last_active timestamp
            session_data["last_active"] = datetime.now().isoformat()
            
            session_key = f"session:{session_id}"
            
            # Try to update in Redis if available
            if self.redis_available:
                try:
                    self.redis_client.setex(
                        session_key,
                        int(self.session_expiry.total_seconds()),
                        json.dumps(session_data)
                    )
                except Exception as e:
                    print(f"Error updating session in Redis: {str(e)}")
                    print("Falling back to in-memory storage")
                    # Disable Redis for future operations
                    self.redis_available = False
            
            # Always update in-memory storage as a backup or if Redis is not available
            self.sessions[session_key] = session_data
            return True
        return False

    def add_emotion_record(self, session_id: str, emotions: Dict[str, float], text: str):
        """Add an emotion analysis record to the session history."""
        session_data = self.get_session(session_id)
        if session_data:
            record = {
                "timestamp": datetime.now().isoformat(),
                "emotions": emotions,
                "text": text
            }
            session_data["emotion_history"].append(record)
            
            # Keep only last 100 records
            if len(session_data["emotion_history"]) > 100:
                session_data["emotion_history"] = session_data["emotion_history"][-100:]
            
            self.update_session(session_id, session_data)
            return True
        return False

    def add_activity_record(self, session_id: str, activity: Dict):
        """Add an activity record to the session history."""
        session_data = self.get_session(session_id)
        if session_data:
            record = {
                "timestamp": datetime.now().isoformat(),
                "activity": activity
            }
            session_data["activity_history"].append(record)
            
            # Keep only last 100 records
            if len(session_data["activity_history"]) > 100:
                session_data["activity_history"] = session_data["activity_history"][-100:]
            
            self.update_session(session_id, session_data)
            return True
        return False

    def get_emotion_trends(self, session_id: str) -> Dict:
        """Get emotion trends from session history."""
        session_data = self.get_session(session_id)
        if not session_data or not session_data["emotion_history"]:
            return {}

        # Calculate emotion frequencies
        emotion_counts = {}
        for record in session_data["emotion_history"]:
            for emotion, score in record["emotions"].items():
                if score > 0.1:  # Only count significant emotions
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Calculate percentages
        total_records = len(session_data["emotion_history"])
        emotion_trends = {
            emotion: (count / total_records) * 100
            for emotion, count in emotion_counts.items()
        }

        return emotion_trends

    def get_activity_preferences(self, session_id: str) -> List[str]:
        """Get user's preferred activities based on history."""
        session_data = self.get_session(session_id)
        if not session_data or not session_data["activity_history"]:
            return []

        # Count activity frequencies
        activity_counts = {}
        for record in session_data["activity_history"]:
            activity = record["activity"]["title"]
            activity_counts[activity] = activity_counts.get(activity, 0) + 1

        # Sort by frequency
        sorted_activities = sorted(
            activity_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [activity for activity, _ in sorted_activities[:5]]

    def update_preferences(self, session_id: str, preferences: Dict):
        """Update user preferences."""
        session_data = self.get_session(session_id)
        if session_data:
            session_data["preferences"].update(preferences)
            self.update_session(session_id, session_data)
            return True
        return False

    def delete_session(self, session_id: str):
        """Delete a session."""
        session_data = self.get_session(session_id)
        if session_data:
            session_key = f"session:{session_id}"
            user_session_key = f"user_sessions:{session_data['user_id']}"
            
            # Try to delete from Redis if available
            if self.redis_available:
                try:
                    # Delete session data
                    self.redis_client.delete(session_key)
                    # Delete user session mapping
                    self.redis_client.delete(user_session_key)
                except Exception as e:
                    print(f"Error deleting session from Redis: {str(e)}")
                    # Disable Redis for future operations
                    self.redis_available = False
            
            # Always delete from in-memory storage
            if session_key in self.sessions:
                del self.sessions[session_key]
            if user_session_key in self.user_sessions:
                del self.user_sessions[user_session_key]
                
            return True
        return False