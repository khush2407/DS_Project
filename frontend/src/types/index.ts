export interface Emotion {
    [key: string]: number;
}

export interface EmotionResponse {
    emotions: Emotion;
    primary_emotion: string;
    summary: string;
}

export interface Activity {
    id: string;
    title: string;
    description: string;
    duration: number;
    difficulty: string;
    categories: string[];
    steps: string[];
    benefits: string[];
    rating?: number;
    created_at?: string;
    emotional_context?: string;
    category?: string;
    progress?: number;
    completed_steps?: number[];
    points?: number;
}

export interface RecommendationResponse {
    activities: Activity[];
    explanation: string;
}

export interface UserPreferences {
    difficulty_level: string;
    preferred_duration: string;
    favorite_activities: string[];
    categories: string[];
    notifications: boolean;
}

export interface SessionResponse {
    session_id: string;
    user_id: string;
    preferences: UserPreferences;
    activity_history: ActivityHistoryItem[];
    created_at: string;
    updated_at: string;
}

export interface EmotionTrendsResponse {
    trends: { [key: string]: number };
    total_records: number;
}

export interface ActivityPreferencesResponse {
    preferred_activities: string[];
    total_activities: number;
}

export interface EmotionAnalysis {
    emotions: Record<string, number>;
    primary_emotion: string;
    summary: string;
}

export interface Recommendation {
    activities: Activity[];
    summary: string;
}

export interface ActivityHistoryItem {
    id: string;
    activity_id: string;
    activity_title: string;
    start_time: string;
    completed_at: string | null;
    completed: boolean;
    progress: number;
    category: string;
    points: number;
    completed_steps: number[];
    mood_level?: number;
    duration: number;
}

export interface Session {
    id: string;
    user_id: string;
    created_at: string;
    last_active: string;
    preferences: UserPreferences;
    emotion_history: EmotionRecord[];
    activity_history: ActivityHistoryItem[];
}

export interface EmotionRecord {
    id: string;
    emotions: Record<string, number>;
    primary_emotion: string;
    timestamp: string;
    text: string;
}

export interface ActivityProgress {
    activity_id: string;
    progress: number;
    last_updated: string;
}

export interface ActivityShare {
    activity_id: string;
    share_token: string;
    expires_at: string;
    access_count: number;
}

export interface ApiResponse<T> {
    data: T;
    message?: string;
    error?: string;
}

export interface ActivityRecommendation {
    activities: Activity[];
    favorites: string[];
    progress: { [key: string]: number };
    history: ActivityHistoryItem[];
}

export interface User {
    id: string;
    email: string;
    username: string;
    full_name?: string;
    created_at: string;
    is_active: boolean;
    is_verified: boolean;
    last_login?: string;
}

export interface Token {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
}

export interface SignupData {
    email: string;
    username: string;
    full_name?: string;
    password: string;
    confirm_password: string;
}

export interface LoginData {
    username: string;
    password: string;
}

export interface ActivityProgressUpdate {
    progress: number;
    completed_steps: number[];
    time_spent: number;
}

export interface ActivityCompletion {
    duration: number;
    completed_steps: number[];
} 