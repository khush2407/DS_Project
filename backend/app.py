from fastapi import FastAPI, HTTPException, Depends, Request, Response, BackgroundTasks, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import logging
import time
from prometheus_client import Counter, Histogram, generate_latest
from services.emotion_service import EmotionService
from services.recommendation_service import RecommendationService
from services.session_service import SessionService
from services.user_service import UserService, UserPreferences, ActivityProgress
from redis import Redis
from models.user import UserCreate, UserResponse, Token
from services.auth_service import auth_service
from services.database import db

# Application settings
class Settings:
    BASE_URL = "http://localhost:3000"  # Frontend URL for sharing

settings = Settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)
logger = logging.getLogger(__name__)

# Prometheus metrics - use a custom registry to avoid duplicate registration
from prometheus_client import CollectorRegistry
from prometheus_client import Counter, Histogram

# Create a custom registry
custom_registry = CollectorRegistry()

# Create metrics with the custom registry
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=custom_registry
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    registry=custom_registry
)

EMOTION_ANALYSIS_COUNT = Counter(
    'emotion_analysis_total',
    'Total emotion analysis requests',
    ['status'],
    registry=custom_registry
)

RECOMMENDATION_COUNT = Counter(
    'recommendation_requests_total',
    'Total recommendation requests',
    ['status'],
    registry=custom_registry
)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info("Connecting to database...")
        await db.connect()
        if db.in_memory_mode:
            logger.info("Using in-memory database mode")
        else:
            logger.info("MongoDB connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    
    yield
    
    # Shutdown
    try:
        logger.info("Closing database connection...")
        if db.client:
            db.client.close()
            logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")

app = FastAPI(
    title="AI Mental Wellness Assistant API",
    description="API for emotion detection and wellness recommendations",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
    expose_headers=["Content-Type", "Authorization"],
)

# Initialize Redis client
redis_client = None
redis_available = False
try:
    redis_client = Redis(
        host='redis',
        port=6379,
        db=0,
        decode_responses=True,
        socket_connect_timeout=2,  # Set a short timeout
        socket_timeout=2
    )
    # Test the connection
    redis_client.ping()
    redis_available = True
    print("Successfully connected to Redis for main application")
except Exception as e:
    print(f"Redis not available: {str(e)}. Using in-memory storage instead.")
    redis_client = None
    redis_available = False

# Initialize services
emotion_service = EmotionService()
recommendation_service = RecommendationService()
session_service = SessionService()
user_service = UserService(redis_client if redis_available else None)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Dependency to get current user - bypassing authentication for development
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Return a mock user instead of verifying the token
    return {
        "user_id": "dev-user-123",
        "email": "dev@example.com"
    }
    # Original authentication code (commented out)
    # return await auth_service.verify_token(token)

class TextInput(BaseModel):
    text: str

class EmotionResponse(BaseModel):
    emotions: Dict[str, float]
    primary_emotion: str
    summary: str

class Activity(BaseModel):
    title: str
    description: str
    duration: str
    difficulty: str
    benefits: List[str]
    steps: List[str]
    emotional_context: str

class RecommendationResponse(BaseModel):
    activities: List[Activity]
    explanation: str

class UserPreferences(BaseModel):
    difficulty_level: Optional[str] = "beginner"
    preferred_duration: Optional[str] = "short"
    favorite_activities: Optional[List[str]] = []

class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    created_at: str
    last_active: str
    preferences: UserPreferences

class EmotionTrendsResponse(BaseModel):
    trends: Dict[str, float]
    total_records: int

class ActivityPreferencesResponse(BaseModel):
    preferred_activities: List[str]
    total_activities: int

class ActivityProgressUpdate(BaseModel):
    progress: float
    completed_steps: List[int]
    time_spent: int

class ActivityCompletion(BaseModel):
    duration: int
    completed_steps: List[int]

class ShareActivityRequest(BaseModel):
    activity_id: str
    platform: str
    message: Optional[str] = None

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {duration:.2f}s"
    )
    
    return response

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to AI Mental Wellness Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "Analyze emotions in text",
            "/recommend": "Get personalized wellness recommendations",
            "/metrics": "View Prometheus metrics",
            "/health": "Check service health"
        }
    }

@app.post("/analyze", response_model=EmotionResponse)
async def analyze_emotion(input_data: TextInput, session_id: Optional[str] = None):
    """
    Analyze the emotion in the provided text.
    Returns detected emotions and their confidence scores.
    """
    logger.info(f"Analyzing emotions for text: {input_data.text[:50]}...")
    
    try:
        # The emotion_service.detect_emotions method already has fallback mechanisms
        # and will return default values even if there's an error
        emotions, primary_emotion = emotion_service.detect_emotions(input_data.text)
        summary = emotion_service.get_emotion_summary(emotions)
        
        # Record emotion analysis in session if session_id is provided
        if session_id:
            try:
                session_service.add_emotion_record(session_id, emotions, input_data.text)
            except Exception as session_error:
                # Log the error but don't fail the request
                logger.error(f"Error recording emotion in session: {str(session_error)}")
        
        EMOTION_ANALYSIS_COUNT.labels(status="success").inc()
        logger.info(f"Emotion analysis successful. Primary emotion: {primary_emotion}")
        
        return {
            "emotions": emotions,
            "primary_emotion": primary_emotion,
            "summary": summary
        }
    except Exception as e:
        # Instead of raising an HTTP exception, use fallback values
        logger.error(f"Error in emotion analysis: {str(e)}")
        EMOTION_ANALYSIS_COUNT.labels(status="error").inc()
        
        # Provide fallback values
        fallback_emotions = {"optimism": 0.5, "joy": 0.3, "caring": 0.2}
        fallback_primary = "optimism"
        fallback_summary = "We couldn't fully analyze your emotions this time. Please try again with more details about how you're feeling."
        
        return {
            "emotions": fallback_emotions,
            "primary_emotion": fallback_primary,
            "summary": fallback_summary
        }

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(emotion_data: EmotionResponse, session_id: Optional[str] = None):
    """
    Get personalized wellness recommendations based on detected emotions.
    """
    logger.info(f"Getting recommendations for emotion: {emotion_data.primary_emotion}")
    
    try:
        # Get user preferences if session exists and is not 'current-session'
        user_preferences = None
        if session_id and session_id != 'current-session':
            try:
                session_data = session_service.get_session(session_id)
                if session_data:
                    user_preferences = session_data["preferences"]
            except Exception as session_error:
                logger.warning(f"Error getting session data: {str(session_error)}")
                # Continue without user preferences
        
        # Get recommendations based on emotions
        recommendations = recommendation_service.get_recommendations(
            emotion_data.emotions,
            emotion_data.primary_emotion,
            user_preferences
            
        )
        
        # Add ID to each activity for frontend compatibility
        for i, activity in enumerate(recommendations):
            if 'id' not in activity:
                # Use the activity title as a basis for the ID
                activity_id = activity['title'].lower().replace(' ', '_')
                activity['id'] = f"{activity_id}_{i}"
        
        explanation = recommendation_service.get_explanation(
            emotion_data.emotions,
            emotion_data.primary_emotion
        )

        # Record recommendations in session if valid session_id is provided
        if session_id and session_id != 'current-session':
            try:
                for activity in recommendations:
                    session_service.add_activity_record(session_id, activity)
            except Exception as e:
                logger.warning(f"Could not record recommendations in session: {str(e)}")
                # Continue without recording in session

        RECOMMENDATION_COUNT.labels(status="success").inc()
        logger.info("Recommendations generated successfully")
        
        return {
            "activities": recommendations,
            "explanation": explanation
        }
    except Exception as e:
        RECOMMENDATION_COUNT.labels(status="error").inc()
        logger.error(f"Error generating recommendations: {str(e)}")
        
        # Provide fallback recommendations instead of failing
        fallback_activities = [
            {
                "id": "deep_breathing_0",
                "title": "Deep Breathing Exercise",
                "description": "A simple breathing technique to help calm your mind and reduce stress.",
                "duration": "5 minutes",
                "difficulty": "beginner",
                "benefits": ["Reduces stress", "Improves focus", "Calms the mind"],
                "steps": [
                    "Find a comfortable seated position",
                    "Close your eyes and breathe naturally",
                    "Inhale deeply through your nose for 4 counts",
                    "Hold your breath for 2 counts",
                    "Exhale slowly through your mouth for 6 counts",
                    "Repeat for 5 minutes"
                ],
                "emotional_context": "This exercise helps with any emotional state"
            },
            {
                "id": "gratitude_journal_1",
                "title": "Gratitude Journaling",
                "description": "Write down things you're grateful for to shift your perspective.",
                "duration": "10 minutes",
                "difficulty": "beginner",
                "benefits": ["Improves mood", "Increases positivity", "Builds resilience"],
                "steps": [
                    "Find a quiet space with a journal or paper",
                    "Write down 3-5 things you're grateful for today",
                    "For each item, write a sentence about why it matters to you",
                    "Reflect on how these positive elements affect your life"
                ],
                "emotional_context": "Helpful for processing difficult emotions"
            }
        ]
        
        fallback_explanation = "These are general wellness activities that can help with a variety of emotional states."
        
        return {
            "activities": fallback_activities,
            "explanation": fallback_explanation
        }

@app.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    return Response(generate_latest(custom_registry), media_type="text/plain")

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify service status.
    """
    try:
        # Check Redis connection if available
        if hasattr(emotion_service, 'redis_available') and emotion_service.redis_available:
            try:
                redis_status = emotion_service.redis_client.ping()
            except Exception:
                redis_status = False
        else:
            redis_status = False
        
        # Check MongoDB connection or in-memory mode
        if db.in_memory_mode:
            mongo_status = True  # In-memory mode is always "operational"
            mongo_service_status = "not available (using in-memory storage)"
        else:
            try:
                mongo_status = await db.client.admin.command('ping') == {'ok': 1.0}
                mongo_service_status = "operational" if mongo_status else "degraded"
            except Exception:
                mongo_status = False
                mongo_service_status = "degraded"
        
        # Check model loading
        model_status = emotion_service.model is not None
        fallback_available = True  # Keyword-based fallback is always available
        
        # Service is healthy if either model is loaded or fallback is available,
        # and either MongoDB is connected or in-memory mode is active
        status = "healthy" if (model_status or fallback_available) and mongo_status else "degraded"
        
        redis_service_status = "operational" if redis_status else "not available (using in-memory storage)"
        emotion_service_status = "operational" if model_status else "operational (using keyword fallback)"
        
        return {
            "status": status,
            "services": {
                "emotion_service": emotion_service_status,
                "recommendation_service": "operational",
                "redis_cache": redis_service_status,
                "mongodb": mongo_service_status
            },
            "in_memory_mode": db.in_memory_mode
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post("/session/create", response_model=SessionResponse)
async def create_session(user_id: str = Query(..., description="User ID for the new session")):
    """Create a new user session."""
    try:
        session_id = session_service.create_session(user_id)
        session_data = session_service.get_session(session_id)
        
        # Add session_id to the response data to match SessionResponse model
        if session_data:
            session_data["session_id"] = session_id
            
        return session_data
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session information."""
    try:
        session_data = session_service.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Add session_id to the response data to match SessionResponse model
        session_data["session_id"] = session_id
        
        return session_data
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session/{session_id}/preferences")
async def update_preferences(session_id: str, preferences: UserPreferences):
    """Update user preferences."""
    try:
        success = session_service.update_preferences(session_id, preferences.dict())
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Preferences updated successfully"}
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}/trends", response_model=EmotionTrendsResponse)
async def get_emotion_trends(session_id: str):
    """Get emotion trends for a session."""
    try:
        trends = session_service.get_emotion_trends(session_id)
        session_data = session_service.get_session(session_id)
        total_records = len(session_data["emotion_history"]) if session_data else 0
        return {
            "trends": trends,
            "total_records": total_records
        }
    except Exception as e:
        logger.error(f"Error getting emotion trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}/preferences", response_model=ActivityPreferencesResponse)
async def get_activity_preferences(session_id: str):
    """Get user's preferred activities."""
    try:
        preferred_activities = session_service.get_activity_preferences(session_id)
        session_data = session_service.get_session(session_id)
        total_activities = len(session_data["activity_history"]) if session_data else 0
        return {
            "preferred_activities": preferred_activities,
            "total_activities": total_activities
        }
    except Exception as e:
        logger.error(f"Error getting activity preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    try:
        success = session_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/activities/{activity_id}/favorite")
async def toggle_favorite(activity_id: str, session_id: str):
    """Toggle favorite status for an activity."""
    try:
        is_favorite = await user_service.toggle_favorite(session_id, activity_id)
        return {"is_favorite": is_favorite}
    except Exception as e:
        logger.error(f"Error toggling favorite: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update favorite status")

@app.get("/api/activities/favorites")
async def get_favorites(session_id: str):
    """Get list of favorite activities."""
    try:
        favorites = await user_service.get_favorites(session_id)
        return {"favorites": favorites}
    except Exception as e:
        logger.error(f"Error getting favorites: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get favorites")

@app.post("/api/activities/{activity_id}/progress")
async def update_activity_progress(
    activity_id: str,
    progress_update: ActivityProgressUpdate,
    session_id: str
):
    """Update activity progress."""
    try:
        progress = await user_service.update_activity_progress(
            session_id,
            activity_id,
            progress_update.progress,
            progress_update.completed_steps,
            progress_update.time_spent
        )
        return progress
    except Exception as e:
        logger.error(f"Error updating progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update progress")

@app.get("/api/activities/{activity_id}/progress")
async def get_activity_progress(activity_id: str, session_id: str):
    """Get activity progress."""
    try:
        progress = await user_service.get_activity_progress(session_id, activity_id)
        if not progress:
            return {"progress": 0, "completed_steps": [], "total_time_spent": 0}
        return progress
    except Exception as e:
        logger.error(f"Error getting progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get progress")

@app.post("/api/activities/{activity_id}/complete")
async def complete_activity(
    activity_id: str,
    completion: ActivityCompletion,
    session_id: str
):
    """Mark activity as completed."""
    try:
        await user_service.add_to_activity_history(
            session_id,
            activity_id,
            completion.duration,
            completion.completed_steps
        )
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error completing activity: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete activity")

@app.get("/api/activities/history")
async def get_activity_history(session_id: str, limit: int = 50):
    """Get activity history."""
    try:
        history = await user_service.get_activity_history(session_id, limit)
        return {"history": history}
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get activity history")

@app.get("/api/activities/recommendations")
async def get_recommendations(session_id: str, limit: int = 5):
    """Get personalized activity recommendations."""
    try:
        # Get all available activities
        all_activities = recommendation_service.get_all_activities()
        
        # Get personalized recommendations
        recommendations = await user_service.generate_recommendations(
            session_id,
            all_activities,
            limit
        )
        
        return {"recommendations": recommendations}
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

@app.post("/api/activities/{activity_id}/share")
async def share_activity(
    activity_id: str,
    share_request: ShareActivityRequest,
    session_id: str
):
    """Share activity on social media."""
    try:
        activity = recommendation_service.get_activity(activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        share_url = f"{settings.BASE_URL}/activities/{activity_id}"
        share_text = share_request.message or f"Check out this wellness activity: {activity['title']}"

        if share_request.platform == "copy":
            return {
                "url": share_url,
                "text": share_text
            }
        elif share_request.platform == "whatsapp":
            return {
                "url": f"https://wa.me/?text={share_text} {share_url}"
            }
        elif share_request.platform == "twitter":
            return {
                "url": f"https://twitter.com/intent/tweet?text={share_text}&url={share_url}"
            }
        elif share_request.platform == "facebook":
            return {
                "url": f"https://www.facebook.com/sharer/sharer.php?u={share_url}"
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid platform")
    except Exception as e:
        logger.error(f"Error sharing activity: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to share activity")

@app.post("/auth/signup", response_model=UserResponse)
async def signup(user_data: UserCreate):
    try:
        user = await auth_service.register_user(user_data)
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            created_at=user.created_at,
            is_active=user.is_active,
            is_verified=user.is_verified,
            last_login=user.last_login
        )
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await auth_service.authenticate_user(form_data.username, form_data.password)
        return auth_service.create_tokens(user.id, user.email)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/auth/refresh", response_model=Token)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    try:
        return auth_service.create_tokens(current_user.user_id, current_user.email)
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    try:
        user_dict = await auth_service.db.get_user_by_id(current_user.user_id)
        if not user_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse(
            id=user_dict["id"],
            email=user_dict["email"],
            username=user_dict["username"],
            full_name=user_dict.get("full_name"),
            created_at=user_dict["created_at"],
            is_active=user_dict.get("is_active", True),
            is_verified=user_dict.get("is_verified", False),
            last_login=user_dict.get("last_login")
        )
    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 