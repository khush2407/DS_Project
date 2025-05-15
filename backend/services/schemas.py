from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class Duration(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"

class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    last_login: Optional[datetime] = None

class UserPreferences(BaseModel):
    difficulty_level: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    preferred_duration: Duration = Field(default=Duration.SHORT)
    favorite_activities: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    notifications: bool = Field(default=True)

    @validator('favorite_activities')
    def validate_favorite_activities(cls, v):
        if len(v) > 50:
            raise ValueError("Maximum 50 favorite activities allowed")
        return v

class ActivityProgress(BaseModel):
    progress: float = Field(ge=0, le=100)
    completed_steps: List[int] = Field(default_factory=list)
    time_spent: int = Field(ge=0)  # in seconds
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class EmotionAnalysis(BaseModel):
    emotions: Dict[str, float]
    primary_emotion: str
    summary: str
    confidence: float = Field(ge=0, le=1)
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ActivityHistory(BaseModel):
    activity_id: str
    activity_title: str
    start_time: datetime
    end_time: datetime
    duration: int  # in minutes
    completed: bool
    progress: float = Field(ge=0, le=100)
    steps_completed: List[int] = Field(default_factory=list)

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v < values['start_time']:
            raise ValueError("End time cannot be before start time")
        return v

class Session(BaseModel):
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    is_active: bool = Field(default=True)

class FavoriteActivity(BaseModel):
    activity_id: str
    added_at: datetime = Field(default_factory=datetime.utcnow)
    category: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    duration: Optional[Duration] = None 