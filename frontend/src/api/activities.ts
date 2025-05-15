import axios from 'axios';
import { Activity, ActivityRecommendation, ApiResponse, ActivityHistoryItem } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getRecommendations = async (): Promise<ActivityRecommendation> => {
  const response = await api.get<ApiResponse<ActivityRecommendation>>('/api/activities/recommendations');
  return response.data.data;
};

export const getActivity = async (id: string): Promise<Activity> => {
  const response = await api.get<ApiResponse<Activity>>(`/api/activities/${id}`);
  return response.data.data;
};

export const startActivity = async (activityId: string): Promise<void> => {
  await api.post<ApiResponse<void>>(`/api/activities/${activityId}/start`);
};

export const updateProgress = async (activityId: string, progress: number): Promise<void> => {
  await api.put<ApiResponse<void>>(`/api/activities/${activityId}/progress`, { progress });
};

export const completeActivity = async (activityId: string): Promise<void> => {
  await api.post<ApiResponse<void>>(`/api/activities/${activityId}/complete`);
};

export const toggleFavorite = async (activityId: string): Promise<void> => {
  await api.post<ApiResponse<void>>(`/api/activities/${activityId}/favorite`);
};

export const shareActivity = async (activityId: string): Promise<string> => {
  const response = await api.post<ApiResponse<{ shareUrl: string }>>(`/api/activities/${activityId}/share`);
  return response.data.data.shareUrl;
};

export const getActivityHistory = async (): Promise<ActivityHistoryItem[]> => {
  const response = await api.get<ApiResponse<ActivityHistoryItem[]>>('/api/activities/history');
  return response.data.data;
};

export const getActivityProgress = async (activityId: string): Promise<number> => {
  const response = await api.get<ApiResponse<{ progress: number }>>(`/api/activities/${activityId}/progress`);
  return response.data.data.progress;
};

export const searchActivities = async (query: string): Promise<Activity[]> => {
  const response = await api.get<ApiResponse<Activity[]>>('/api/activities/search', {
    params: { q: query },
  });
  return response.data.data;
};

export const getFavorites = async (): Promise<string[]> => {
  const response = await api.get<ApiResponse<string[]>>('/api/activities/favorites');
  return response.data.data;
}; 