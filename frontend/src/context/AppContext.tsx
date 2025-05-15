import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { createSession, getSession, updatePreferences, getActivity, startActivity, completeActivity as completeActivityApi } from '../services/api';
import { UserPreferences, SessionResponse, ActivityHistoryItem, Activity } from '../types';

/**
 * Interface defining the shape of the application context
 * @interface AppContextType
 * @property {string | null} sessionId - Current session ID
 * @property {UserPreferences} preferences - User preferences for activities and notifications
 * @property {Activity | null} activeActivity - Currently active activity
 * @property {ActivityHistoryItem[]} activityHistory - List of completed activities
 * @property {boolean} isLoading - Loading state indicator
 * @property {string | null} error - Current error message
 * @property {Function} startActivity - Start a new activity
 * @property {Function} completeActivity - Complete the current activity
 * @property {Function} updateUserPreferences - Update user preferences
 * @property {Function} clearError - Clear current error
 * @property {Function} refreshActivityHistory - Refresh activity history from server
 * @property {Function} getActivityProgress - Get progress for a specific activity
 * @property {Function} updateActivityProgress - Update progress for a specific activity
 * @property {Function} getActivityStats - Get activity statistics
 * @property {Function} resetSession - Reset session and clear all data
 * @property {Function} getStreakInfo - Get user's activity streak information
 * @property {Function} getCategoryStats - Get statistics for each activity category
 * @property {Function} getTimeBasedStats - Get time-based activity statistics
 * @property {Function} getRecommendationStats - Get statistics for activity recommendations
 */
interface AppContextType {
    sessionId: string | null;
    preferences: UserPreferences;
    activeActivity: Activity | null;
    activityHistory: ActivityHistoryItem[];
    isLoading: boolean;
    error: string | null;
    startActivity: (activityId: string) => Promise<void>;
    completeActivity: (activityId: string, moodLevel: number) => Promise<void>;
    updateUserPreferences: (preferences: UserPreferences) => Promise<void>;
    clearError: () => void;
    refreshActivityHistory: () => Promise<void>;
    getActivityProgress: (activityId: string) => number;
    updateActivityProgress: (activityId: string, progress: number) => void;
    getActivityStats: () => ActivityStats;
    resetSession: () => Promise<void>;
    getStreakInfo: () => StreakInfo;
    getCategoryStats: () => CategoryStats;
    getTimeBasedStats: () => TimeBasedStats;
    getRecommendationStats: () => RecommendationStats;
}

/**
 * Interface for activity statistics
 * @interface ActivityStats
 */
interface ActivityStats {
    totalActivities: number;
    completedActivities: number;
    totalDuration: number;
    averageDuration: number;
    mostFrequentCategory: string;
    completionRate: number;
    longestStreak: number;
    currentStreak: number;
    totalPoints: number;
    averagePointsPerActivity: number;
}

/**
 * Interface for streak information
 * @interface StreakInfo
 */
interface StreakInfo {
    currentStreak: number;
    longestStreak: number;
    lastActivityDate: string | null;
    streakStartDate: string | null;
    streakHistory: { date: string; count: number }[];
}

/**
 * Interface for category statistics
 * @interface CategoryStats
 */
interface CategoryStats {
    categories: {
        [key: string]: {
            count: number;
            totalDuration: number;
            averageDuration: number;
            completionRate: number;
            lastActivity: string | null;
        };
    };
    mostFrequentCategory: string;
    leastFrequentCategory: string;
    categoryDistribution: { category: string; percentage: number }[];
}

/**
 * Interface for time-based statistics
 * @interface TimeBasedStats
 */
interface TimeBasedStats {
    dailyStats: {
        [date: string]: {
            count: number;
            duration: number;
            categories: string[];
        };
    };
    weeklyStats: {
        [week: string]: {
            count: number;
            duration: number;
            averageDuration: number;
        };
    };
    monthlyStats: {
        [month: string]: {
            count: number;
            duration: number;
            mostActiveDay: string;
        };
    };
    bestTimeOfDay: string;
    mostActiveDay: string;
}

/**
 * Interface for recommendation statistics
 * @interface RecommendationStats
 */
interface RecommendationStats {
    totalRecommendations: number;
    acceptedRecommendations: number;
    recommendationAccuracy: number;
    categoryPreferences: {
        [category: string]: {
            recommended: number;
            accepted: number;
            accuracy: number;
        };
    };
    timeBasedPreferences: {
        [timeOfDay: string]: {
            recommended: number;
            accepted: number;
            accuracy: number;
        };
    };
}

const defaultPreferences: UserPreferences = {
    difficulty_level: 'beginner',
    preferred_duration: 'short',
    favorite_activities: [],
    categories: [],
    notifications: true
};

const AppContext = createContext<AppContextType | undefined>(undefined);

/**
 * Provider component for the application context
 */
export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [preferences, setPreferences] = useState<UserPreferences>(defaultPreferences);
    const [activeActivity, setActiveActivity] = useState<Activity | null>(null);
    const [activityHistory, setActivityHistory] = useState<ActivityHistoryItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activityProgress, setActivityProgress] = useState<Record<string, number>>({});
    const [startTime, setStartTime] = useState<Date | null>(null);
    const [completedSteps, setCompletedSteps] = useState<string[]>([]);

    /**
     * Initialize the session and load saved data
     */
    const initializeSession = useCallback(async () => {
        try {
            setIsLoading(true);
            const storedSessionId = localStorage.getItem('sessionId');
            
            if (storedSessionId) {
                const session = await getSession(storedSessionId);
                setSessionId(session.session_id);
                setPreferences(session.preferences);
                
                // Load saved data from localStorage
                const loadSavedData = () => {
                    try {
                        const storedHistory = localStorage.getItem('activityHistory');
                        if (storedHistory) {
                            setActivityHistory(JSON.parse(storedHistory));
                        }

                        const storedProgress = localStorage.getItem('activityProgress');
                        if (storedProgress) {
                            setActivityProgress(JSON.parse(storedProgress));
                        }

                        const storedPreferences = localStorage.getItem('userPreferences');
                        if (storedPreferences) {
                            setPreferences(JSON.parse(storedPreferences));
                        }
                    } catch (err) {
                        console.error('Error loading saved data:', err);
                        setError('Failed to load saved data');
                    }
                };

                loadSavedData();
            } else {
                const newSession = await createSession('user-' + Date.now());
                setSessionId(newSession.session_id);
                localStorage.setItem('sessionId', newSession.session_id);
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to initialize session';
            setError(errorMessage);
            console.error('Session initialization error:', err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        initializeSession();
    }, [initializeSession]);

    /**
     * Refresh activity history from the server
     */
    const refreshActivityHistory = useCallback(async () => {
        if (!sessionId) {
            setError('No active session');
            return;
        }
        
        try {
            setIsLoading(true);
            const session = await getSession(sessionId);
            if (session.activityHistory) {
                setActivityHistory(session.activityHistory);
                localStorage.setItem('activityHistory', JSON.stringify(session.activityHistory));
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to refresh activity history';
            setError(errorMessage);
            console.error('Activity history refresh error:', err);
        } finally {
            setIsLoading(false);
        }
    }, [sessionId]);

    /**
     * Start a new activity
     */
    const startActivity = async (activityId: string) => {
        try {
            setIsLoading(true);
            const activity = await getActivity(activityId);
            if (!activity) {
                throw new Error('Activity not found');
            }

            const startTime = new Date();
            setStartTime(startTime);
            setActiveActivity(activity);
            setCompletedSteps([]);

            const newActivity: ActivityHistoryItem = {
                id: Date.now().toString(),
                activity_id: activity.id,
                activity_title: activity.title,
                start_time: startTime.toISOString(),
                completed_at: null,
                duration: 0,
                completed: false,
                progress: 0,
                category: activity.category || activity.categories[0] || 'general',
                points: 0,
                completed_steps: []
            };

            setActivityHistory(prev => [...prev, newActivity]);
            await startActivity(activityId);
        } catch (error) {
            console.error('Error starting activity:', error);
            setError(error instanceof Error ? error.message : 'Failed to start activity');
        } finally {
            setIsLoading(false);
        }
    };

    /**
     * Get streak information for the user
     * @returns {StreakInfo} Information about the user's activity streaks
     */
    const getStreakInfo = useCallback((): StreakInfo => {
        const today = new Date();
        const streakHistory: { date: string; count: number }[] = [];
        let currentStreak = 0;
        let longestStreak = 0;
        let lastActivityDate: string | null = null;
        let streakStartDate: string | null = null;

        // Sort activities by date
        const sortedActivities = [...activityHistory].sort((a, b) => 
            new Date(b.start_time).getTime() - new Date(a.start_time).getTime()
        );

        if (sortedActivities.length > 0) {
            lastActivityDate = sortedActivities[0].start_time;
            let currentDate = new Date(lastActivityDate);
            let previousDate = new Date(lastActivityDate);

            // Calculate streaks
            for (const activity of sortedActivities) {
                const activityDate = new Date(activity.start_time);
                const dayDiff = Math.floor((previousDate.getTime() - activityDate.getTime()) / (1000 * 60 * 60 * 24));

                if (dayDiff <= 1) {
                    currentStreak++;
                    if (currentStreak > longestStreak) {
                        longestStreak = currentStreak;
                        streakStartDate = activity.start_time;
                    }
                } else {
                    currentStreak = 1;
                }

                previousDate = activityDate;
            }
        }

        return {
            currentStreak,
            longestStreak,
            lastActivityDate,
            streakStartDate,
            streakHistory
        };
    }, [activityHistory]);

    /**
     * Get activity statistics
     */
    const getActivityStats = useCallback((): ActivityStats => {
        const completedActivities = activityHistory.filter(activity => activity.completed);
        const totalDuration = completedActivities.reduce((sum, activity) => sum + activity.duration, 0);
        const categoryCounts = completedActivities.reduce((counts, activity) => {
            counts[activity.category] = (counts[activity.category] || 0) + 1;
            return counts;
        }, {} as Record<string, number>);

        const mostFrequentCategory = Object.entries(categoryCounts)
            .sort(([, a], [, b]) => b - a)[0]?.[0] || 'None';

        const { longestStreak, currentStreak } = getStreakInfo();

        return {
            totalActivities: activityHistory.length,
            completedActivities: completedActivities.length,
            totalDuration,
            averageDuration: completedActivities.length ? totalDuration / completedActivities.length : 0,
            mostFrequentCategory,
            completionRate: activityHistory.length ? (completedActivities.length / activityHistory.length) * 100 : 0,
            longestStreak,
            currentStreak,
            totalPoints: completedActivities.reduce((sum, activity) => sum + (activity.points || 0), 0),
            averagePointsPerActivity: completedActivities.length ? 
                completedActivities.reduce((sum, activity) => sum + (activity.points || 0), 0) / completedActivities.length : 0
        };
    }, [activityHistory, getStreakInfo]);

    /**
     * Complete the current activity
     */
    const completeActivity = async (activityId: string, moodLevel: number) => {
        try {
            setIsLoading(true);
            const activeActivity = activityHistory.find(a => a.id === activityId);
            if (!activeActivity || !startTime) {
                throw new Error('Activity not found or not started');
            }

            const endTime = new Date();
            const sessionId = localStorage.getItem('sessionId') || 'current-session';
            const durationInSeconds = Math.round((endTime.getTime() - startTime.getTime()) / 1000);
            const completedSteps: number[] = [];
            
            await completeActivityApi(activityId, sessionId, durationInSeconds, completedSteps);

            const newActivity: ActivityHistoryItem = {
                id: Date.now().toString(),
                activity_id: activeActivity.id,
                activity_title: activeActivity.activity_title,
                start_time: startTime.toISOString(),
                completed_at: endTime.toISOString(),
                completed: true,
                progress: 1,
                category: activeActivity.category,
                points: Math.floor(moodLevel * 10),
                completed_steps: [],
                mood_level: moodLevel,
                duration: durationInSeconds
            };

            setActivityHistory(prev => [...prev, newActivity]);
            setActiveActivity(null);
            setStartTime(null);
            setCompletedSteps([]);
        } catch (error) {
            console.error('Error completing activity:', error);
            setError(error instanceof Error ? error.message : 'Failed to complete activity');
        } finally {
            setIsLoading(false);
        }
    };

    /**
     * Update user preferences
     */
    const updateUserPreferences = async (newPreferences: UserPreferences) => {
        try {
            setIsLoading(true);
            if (!sessionId) throw new Error('No active session');
            
            await updatePreferences(sessionId, newPreferences);
            setPreferences(newPreferences);
            localStorage.setItem('userPreferences', JSON.stringify(newPreferences));
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to update preferences';
            setError(errorMessage);
            console.error('Preferences update error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    /**
     * Get progress for a specific activity
     */
    const getActivityProgress = (activityId: string) => {
        return activityProgress[activityId] || 0;
    };

    /**
     * Update progress for a specific activity
     */
    const updateActivityProgress = (activityId: string, progress: number) => {
        setActivityProgress(prev => {
            const updated = { ...prev, [activityId]: progress };
            localStorage.setItem('activityProgress', JSON.stringify(updated));
            return updated;
        });
    };

    /**
     * Reset session and clear all data
     */
    const resetSession = async () => {
        try {
            setIsLoading(true);
            localStorage.removeItem('sessionId');
            localStorage.removeItem('activityHistory');
            localStorage.removeItem('activityProgress');
            localStorage.removeItem('userPreferences');
            
            setSessionId(null);
            setActivityHistory([]);
            setActivityProgress({});
            setPreferences(defaultPreferences);
            setActiveActivity(null);
            setStartTime(null);
            setCompletedSteps([]);
            
            await initializeSession();
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Failed to reset session';
            setError(errorMessage);
            console.error('Session reset error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const clearError = () => setError(null);

    /**
     * Get statistics for each activity category
     * @returns {CategoryStats} Statistics for each activity category
     */
    const getCategoryStats = useCallback((): CategoryStats => {
        const categoryStats: CategoryStats['categories'] = {};
        let totalActivities = 0;

        // Calculate category statistics
        activityHistory.forEach(activity => {
            const category = activity.activity_title.split(' ')[0];
            if (!categoryStats[category]) {
                categoryStats[category] = {
                    count: 0,
                    totalDuration: 0,
                    averageDuration: 0,
                    completionRate: 0,
                    lastActivity: null
                };
            }

            categoryStats[category].count++;
            categoryStats[category].totalDuration += activity.duration;
            categoryStats[category].averageDuration = 
                categoryStats[category].totalDuration / categoryStats[category].count;
            categoryStats[category].completionRate = 
                (activity.completed ? 1 : 0) / categoryStats[category].count;
            categoryStats[category].lastActivity = activity.start_time;
            totalActivities++;
        });

        // Calculate category distribution
        const categoryDistribution = Object.entries(categoryStats).map(([category, stats]) => ({
            category,
            percentage: (stats.count / totalActivities) * 100
        }));

        // Find most and least frequent categories
        const sortedCategories = Object.entries(categoryStats)
            .sort(([, a], [, b]) => b.count - a.count);
        const mostFrequentCategory = sortedCategories[0]?.[0] || 'None';
        const leastFrequentCategory = sortedCategories[sortedCategories.length - 1]?.[0] || 'None';

        return {
            categories: categoryStats,
            mostFrequentCategory,
            leastFrequentCategory,
            categoryDistribution
        };
    }, [activityHistory]);

    /**
     * Get time-based activity statistics
     * @returns {TimeBasedStats} Time-based statistics for activities
     */
    const getTimeBasedStats = useCallback((): TimeBasedStats => {
        const dailyStats: TimeBasedStats['dailyStats'] = {};
        const weeklyStats: TimeBasedStats['weeklyStats'] = {};
        const monthlyStats: TimeBasedStats['monthlyStats'] = {};
        const timeOfDayCounts: { [key: string]: number } = {};
        const dayOfWeekCounts: { [key: string]: number } = {};

        activityHistory.forEach(activity => {
            const date = new Date(activity.start_time);
            const dayKey = date.toISOString().split('T')[0];
            const weekKey = `${date.getFullYear()}-W${Math.ceil((date.getDate() + date.getDay()) / 7)}`;
            const monthKey = `${date.getFullYear()}-${date.getMonth() + 1}`;
            const timeOfDay = date.getHours() < 12 ? 'morning' : 
                            date.getHours() < 17 ? 'afternoon' : 'evening';
            const dayOfWeek = date.toLocaleDateString('en-US', { weekday: 'long' });

            // Update daily stats
            if (!dailyStats[dayKey]) {
                dailyStats[dayKey] = { count: 0, duration: 0, categories: [] };
            }
            dailyStats[dayKey].count++;
            dailyStats[dayKey].duration += activity.duration;
            if (!dailyStats[dayKey].categories.includes(activity.activity_title.split(' ')[0])) {
                dailyStats[dayKey].categories.push(activity.activity_title.split(' ')[0]);
            }

            // Update weekly stats
            if (!weeklyStats[weekKey]) {
                weeklyStats[weekKey] = { count: 0, duration: 0, averageDuration: 0 };
            }
            weeklyStats[weekKey].count++;
            weeklyStats[weekKey].duration += activity.duration;
            weeklyStats[weekKey].averageDuration = 
                weeklyStats[weekKey].duration / weeklyStats[weekKey].count;

            // Update monthly stats
            if (!monthlyStats[monthKey]) {
                monthlyStats[monthKey] = { count: 0, duration: 0, mostActiveDay: '' };
            }
            monthlyStats[monthKey].count++;
            monthlyStats[monthKey].duration += activity.duration;

            // Update time of day counts
            timeOfDayCounts[timeOfDay] = (timeOfDayCounts[timeOfDay] || 0) + 1;
            dayOfWeekCounts[dayOfWeek] = (dayOfWeekCounts[dayOfWeek] || 0) + 1;
        });

        // Find best time of day and most active day
        const bestTimeOfDay = Object.entries(timeOfDayCounts)
            .sort(([, a], [, b]) => b - a)[0]?.[0] || 'unknown';
        const mostActiveDay = Object.entries(dayOfWeekCounts)
            .sort(([, a], [, b]) => b - a)[0]?.[0] || 'unknown';

        return {
            dailyStats,
            weeklyStats,
            monthlyStats,
            bestTimeOfDay,
            mostActiveDay
        };
    }, [activityHistory]);

    /**
     * Get statistics for activity recommendations
     * @returns {RecommendationStats} Statistics for activity recommendations
     */
    const getRecommendationStats = useCallback((): RecommendationStats => {
        const categoryPreferences: RecommendationStats['categoryPreferences'] = {};
        const timeBasedPreferences: RecommendationStats['timeBasedPreferences'] = {};
        let totalRecommendations = 0;
        let acceptedRecommendations = 0;

        // Calculate recommendation statistics
        activityHistory.forEach(activity => {
            const category = activity.activity_title.split(' ')[0];
            const timeOfDay = new Date(activity.start_time).getHours() < 12 ? 'morning' : 
                            new Date(activity.start_time).getHours() < 17 ? 'afternoon' : 'evening';

            // Update category preferences
            if (!categoryPreferences[category]) {
                categoryPreferences[category] = {
                    recommended: 0,
                    accepted: 0,
                    accuracy: 0
                };
            }
            categoryPreferences[category].recommended++;
            if (activity.completed) {
                categoryPreferences[category].accepted++;
            }
            categoryPreferences[category].accuracy = 
                (categoryPreferences[category].accepted / categoryPreferences[category].recommended) * 100;

            // Update time-based preferences
            if (!timeBasedPreferences[timeOfDay]) {
                timeBasedPreferences[timeOfDay] = {
                    recommended: 0,
                    accepted: 0,
                    accuracy: 0
                };
            }
            timeBasedPreferences[timeOfDay].recommended++;
            if (activity.completed) {
                timeBasedPreferences[timeOfDay].accepted++;
            }
            timeBasedPreferences[timeOfDay].accuracy = 
                (timeBasedPreferences[timeOfDay].accepted / timeBasedPreferences[timeOfDay].recommended) * 100;

            totalRecommendations++;
            if (activity.completed) {
                acceptedRecommendations++;
            }
        });

        return {
            totalRecommendations,
            acceptedRecommendations,
            recommendationAccuracy: (acceptedRecommendations / totalRecommendations) * 100,
            categoryPreferences,
            timeBasedPreferences
        };
    }, [activityHistory]);

    const value = {
        sessionId,
        preferences,
        activeActivity,
        activityHistory,
        isLoading,
        error,
        startActivity,
        completeActivity,
        updateUserPreferences,
        clearError,
        refreshActivityHistory,
        getActivityProgress,
        updateActivityProgress,
        getActivityStats,
        resetSession,
        getStreakInfo,
        getCategoryStats,
        getTimeBasedStats,
        getRecommendationStats
    };

    return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

/**
 * Hook to use the application context
 * @returns {AppContextType} The application context
 * @throws {Error} If used outside of AppProvider
 * @example
 * ```tsx
 * const MyComponent = () => {
 *   const { 
 *     activeActivity,
 *     startActivity,
 *     getActivityStats
 *   } = useApp();
 * 
 *   const stats = getActivityStats();
 *   console.log(`Completed ${stats.completedActivities} activities`);
 * 
 *   return (
 *     <div>
 *       {activeActivity ? (
 *         <p>Currently doing: {activeActivity.title}</p>
 *       ) : (
 *         <button onClick={() => startActivity('some-id')}>
 *           Start Activity
 *         </button>
 *       )}
 *     </div>
 *   );
 * };
 */
export const useApp = () => {
    const context = useContext(AppContext);
    if (context === undefined) {
        throw new Error('useApp must be used within an AppProvider');
    }
    return context;
}; 