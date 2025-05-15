import axios from 'axios';
import {
    EmotionResponse,
    RecommendationResponse,
    SessionResponse,
    EmotionTrendsResponse,
    ActivityPreferencesResponse,
    UserPreferences,
    Activity,
    ActivityHistoryItem
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: true, // Important for CORS requests with credentials
    timeout: 10000, // Add timeout to prevent hanging requests
});

// Add request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        // Skip authentication for now - allow all requests without tokens
        // const token = localStorage.getItem('access_token');
        // if (token) {
        //     config.headers.Authorization = `Bearer ${token}`;
        // }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Add response interceptor to handle token refresh and network errors
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        // Handle network errors (no response from server)
        if (!error.response) {
            console.error('Network error:', error);
            return Promise.reject(error);
        }
        
        const originalRequest = error.config;

        // If error is 401 and we haven't tried to refresh token yet
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                // Use the configured api instance instead of direct axios call
                const response = await api.post('/auth/refresh', null, {
                    headers: {
                        Authorization: `Bearer ${refreshToken}`,
                    },
                });

                const { access_token, refresh_token } = response.data;
                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', refresh_token);

                // Retry the original request with new token
                originalRequest.headers.Authorization = `Bearer ${access_token}`;
                return api(originalRequest);
            } catch (refreshError) {
                // If refresh token fails, redirect to login
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

// Auth API endpoints
export const signup = async (userData: {
    email: string;
    username: string;
    full_name?: string;
    password: string;
    confirm_password: string;
}) => {
    const response = await api.post('/auth/signup', userData);
    return response.data;
};

export const login = async (credentials: {
    username: string;
    password: string;
}) => {
    // Use URLSearchParams instead of FormData for OAuth2 password flow
    const params = new URLSearchParams();
    params.append('username', credentials.username);
    params.append('password', credentials.password);

    const response = await api.post('/auth/login', params, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    });
    return response.data;
};

export const getCurrentUser = async () => {
    const response = await api.get('/auth/me');
    return response.data;
};

// Session API endpoints
export const createSession = async (userId: string) => {
    const response = await api.post(`/session/create?user_id=${userId}`);
    return response.data;
};

export const getSession = async (sessionId: string) => {
    const response = await api.get(`/session/${sessionId}`);
    return response.data;
};

export const updatePreferences = async (sessionId: string, preferences: any) => {
    const response = await api.post(`/session/${sessionId}/preferences`, preferences);
    return response.data;
};

// Emotion Analysis API endpoints
export const analyzeEmotion = async (text: string, sessionId?: string) => {
    const response = await api.post('/analyze', { text }, {
        params: { session_id: sessionId },
    });
    return response.data;
};

export const getRecommendations = async (emotionData: any, sessionId?: string) => {
    const response = await api.post('/recommend', emotionData, {
        params: { session_id: sessionId },
    });
    return response.data;
};

// Activity API endpoints
export const toggleFavorite = async (activityId: string, sessionId: string) => {
    const response = await api.post(`/api/activities/${activityId}/favorite`, null, {
        params: { session_id: sessionId },
    });
    return response.data;
};

export const getFavorites = async (sessionId: string) => {
    const response = await api.get('/api/activities/favorites', {
        params: { session_id: sessionId },
    });
    return response.data;
};

export const updateActivityProgress = async (
    activityId: string,
    sessionId: string,
    progress: number,
    completedSteps: number[],
    timeSpent: number
) => {
    const response = await api.post(`/api/activities/${activityId}/progress`, {
        progress,
        completed_steps: completedSteps,
        time_spent: timeSpent,
    }, {
        params: { session_id: sessionId },
    });
    return response.data;
};

export const completeActivity = async (
    activityId: string,
    sessionId: string,
    duration: number,
    completedSteps: number[]
) => {
    const response = await api.post(`/api/activities/${activityId}/complete`, {
        duration,
        completed_steps: completedSteps,
    }, {
        params: { session_id: sessionId },
    });
    return response.data;
};

export const getActivityHistory = async (sessionId: string, limit: number = 50) => {
    const response = await api.get('/api/activities/history', {
        params: { session_id: sessionId, limit },
    });
    return response.data;
};

export const getActivityRecommendations = async (sessionId: string, limit: number = 5) => {
    const response = await api.get('/api/activities/recommendations', {
        params: { session_id: sessionId, limit },
    });
    return response.data;
};

export const shareActivity = async (
    activityId: string,
    sessionId: string,
    platform: string,
    message?: string
) => {
    const response = await api.post(`/api/activities/${activityId}/share`, {
        platform,
        message,
    }, {
        params: { session_id: sessionId },
    });
    return response.data;
};

export const getActivity = async (activityId: string) => {
    const response = await api.get(`/api/activities/${activityId}`);
    return response.data;
};

export const startActivity = async (activityId: string) => {
    const response = await api.post(`/api/activities/${activityId}/start`);
    return response.data;
};

export const getEmotionTrends = async (sessionId: string): Promise<{ date: string; emotion: string; score: number }[]> => {
    const response = await api.get(`/session/${sessionId}/trends`);
    return response.data;
};

export const getActivityPreferences = async (sessionId: string): Promise<UserPreferences> => {
    const response = await api.get(`/session/${sessionId}/preferences`);
    return response.data;
};

export const deleteSession = async (sessionId: string): Promise<void> => {
    await api.delete(`/session/${sessionId}`);
};