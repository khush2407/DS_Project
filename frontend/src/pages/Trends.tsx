import React, { useEffect, useState } from 'react';
import {
    Container,
    Box,
    Typography,
    Paper,
    Grid,
    CircularProgress,
    useTheme,
} from '@mui/material';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { motion } from 'framer-motion';
import { EmotionTrendsResponse, ActivityHistoryItem } from '../types';
import { getActivityHistory } from '../api/activities';

// Register ChartJS components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
);

const Trends: React.FC = () => {
    const theme = useTheme();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [history, setHistory] = useState<ActivityHistoryItem[]>([]);
    const [emotionTrends, setEmotionTrends] = useState<EmotionTrendsResponse | null>(null);
    const [moodData, setMoodData] = useState<number[]>([]);
    const [moodLabels, setMoodLabels] = useState<string[]>([]);

    useEffect(() => {
        // Generate dummy data instead of fetching from API
        generateDummyData();
    }, []);

    const generateDummyData = () => {
        // Dummy activity history data
        const dummyHistory: ActivityHistoryItem[] = [
            {
                id: '1',
                activity_id: 'act1',
                activity_title: 'Morning Meditation',
                start_time: '2025-05-07T08:00:00Z',
                completed_at: '2025-05-07T08:15:00Z',
                completed: true,
                progress: 100,
                category: 'Mindfulness',
                points: 10,
                completed_steps: [1, 2, 3],
                mood_level: 4,
                duration: 15
            },
            {
                id: '2',
                activity_id: 'act2',
                activity_title: 'Journaling',
                start_time: '2025-05-08T09:00:00Z',
                completed_at: '2025-05-08T09:20:00Z',
                completed: true,
                progress: 100,
                category: 'Self-reflection',
                points: 15,
                completed_steps: [1, 2, 3, 4],
                mood_level: 4.5,
                duration: 20
            },
            {
                id: '3',
                activity_id: 'act3',
                activity_title: 'Yoga Session',
                start_time: '2025-05-09T07:30:00Z',
                completed_at: '2025-05-09T08:00:00Z',
                completed: true,
                progress: 100,
                category: 'Physical',
                points: 20,
                completed_steps: [1, 2, 3, 4, 5],
                mood_level: 5,
                duration: 30
            },
            {
                id: '4',
                activity_id: 'act4',
                activity_title: 'Breathing Exercise',
                start_time: '2025-05-10T18:00:00Z',
                completed_at: '2025-05-10T18:10:00Z',
                completed: true,
                progress: 100,
                category: 'Stress Relief',
                points: 8,
                completed_steps: [1, 2],
                mood_level: 3.5,
                duration: 10
            },
            {
                id: '5',
                activity_id: 'act5',
                activity_title: 'Gratitude Practice',
                start_time: '2025-05-11T21:00:00Z',
                completed_at: '2025-05-11T21:15:00Z',
                completed: true,
                progress: 100,
                category: 'Positivity',
                points: 12,
                completed_steps: [1, 2, 3],
                mood_level: 4.2,
                duration: 15
            },
            {
                id: '6',
                activity_id: 'act6',
                activity_title: 'Nature Walk',
                start_time: '2025-05-12T16:00:00Z',
                completed_at: '2025-05-12T16:45:00Z',
                completed: true,
                progress: 100,
                category: 'Physical',
                points: 25,
                completed_steps: [1, 2, 3],
                mood_level: 4.8,
                duration: 45
            },
            {
                id: '7',
                activity_id: 'act7',
                activity_title: 'Self-care Routine',
                start_time: '2025-05-13T20:00:00Z',
                completed_at: null,
                completed: false,
                progress: 50,
                category: 'Self-care',
                points: 0,
                completed_steps: [1, 2],
                mood_level: 3.8,
                duration: 30
            }
        ];

        // Dummy emotion trends data
        const dummyEmotionTrends: EmotionTrendsResponse = {
            trends: {
                'joy': 35,
                'gratitude': 25,
                'calm': 20,
                'hope': 15,
                'anxiety': 5
            },
            total_records: 100
        };

        // Dummy mood data for the past week
        const dummyMoodData = [3.5, 4.0, 4.2, 3.8, 4.5, 4.8, 4.2];
        const dummyMoodLabels = [
            'May 7', 'May 8', 'May 9', 'May 10', 'May 11', 'May 12', 'May 13'
        ];

        setHistory(dummyHistory);
        setEmotionTrends(dummyEmotionTrends);
        setMoodData(dummyMoodData);
        setMoodLabels(dummyMoodLabels);
        setLoading(false);
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
        });
    };

    const activityCompletionData = {
        labels: history.map(item => formatDate(item.start_time)),
        datasets: [
            {
                label: 'Activity Completion',
                data: history.map(item => item.completed ? 1 : 0),
                borderColor: theme.palette.primary.main,
                backgroundColor: theme.palette.primary.light,
                tension: 0.4,
            },
        ],
    };

    const activityDurationData = {
        labels: history.map(item => formatDate(item.start_time)),
        datasets: [
            {
                label: 'Duration (minutes)',
                data: history.map(item => item.duration || 0),
                borderColor: theme.palette.secondary.main,
                backgroundColor: theme.palette.secondary.light,
                tension: 0.4,
            },
        ],
    };

    const completionRateData = {
        labels: ['Completed', 'In Progress'],
        datasets: [
            {
                data: [
                    history.filter(item => item.completed).length,
                    history.filter(item => !item.completed).length,
                ],
                backgroundColor: [
                    theme.palette.success.main,
                    theme.palette.warning.main,
                ],
            },
        ],
    };

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top' as const,
            },
        },
        scales: {
            y: {
                beginAtZero: true,
            },
        },
    };

    const pageVariants = {
        hidden: { opacity: 0 },
        visible: { opacity: 1 },
    };

    if (loading) {
        return (
            <Box
                sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    minHeight: '60vh',
                }}
            >
                <CircularProgress />
            </Box>
        );
    }

    // Create data for emotion distribution chart
    const emotionDistributionData = {
        labels: emotionTrends ? Object.keys(emotionTrends.trends) : [],
        datasets: [
            {
                label: 'Emotion Distribution',
                data: emotionTrends ? Object.values(emotionTrends.trends) : [],
                backgroundColor: [
                    theme.palette.primary.light,
                    theme.palette.secondary.light,
                    theme.palette.success.light,
                    theme.palette.info.light,
                    theme.palette.warning.light,
                ],
                borderColor: [
                    theme.palette.primary.main,
                    theme.palette.secondary.main,
                    theme.palette.success.main,
                    theme.palette.info.main,
                    theme.palette.warning.main,
                ],
                borderWidth: 1,
            },
        ],
    };

    // Create data for mood tracking chart
    const moodTrackingData = {
        labels: moodLabels,
        datasets: [
            {
                label: 'Mood Level',
                data: moodData,
                borderColor: theme.palette.primary.main,
                backgroundColor: 'rgba(255, 107, 152, 0.2)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: theme.palette.primary.main,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
            },
        ],
    };

    // Create data for activity category distribution
    const categoryData = {
        labels: ['Mindfulness', 'Self-reflection', 'Physical', 'Stress Relief', 'Positivity', 'Self-care'],
        datasets: [
            {
                label: 'Activities by Category',
                data: [1, 1, 2, 1, 1, 1],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.7)',
                    'rgba(54, 162, 235, 0.7)',
                    'rgba(255, 206, 86, 0.7)',
                    'rgba(75, 192, 192, 0.7)',
                    'rgba(153, 102, 255, 0.7)',
                    'rgba(255, 159, 64, 0.7)',
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                ],
                borderWidth: 1,
            },
        ],
    };

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            <motion.div
                variants={pageVariants}
                initial="hidden"
                animate="visible"
            >
                <Box sx={{ mb: 4 }}>
                    <Typography variant="h4" component="h1" gutterBottom>
                        Emotion Trends
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                        Track your emotional well-being and activity patterns
                    </Typography>
                </Box>

                <Grid container spacing={3}>
                    {/* Mood Tracking Chart */}
                    <Grid item xs={12}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                Mood Tracking
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Your daily mood levels over the past week
                            </Typography>
                            <Line data={moodTrackingData} options={chartOptions} />
                        </Paper>
                    </Grid>

                    {/* Emotion Distribution Chart */}
                    <Grid item xs={12} md={6}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                Emotion Distribution
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Breakdown of your emotional states
                            </Typography>
                            <Box sx={{ height: 300 }}>
                                <Doughnut data={emotionDistributionData} options={chartOptions} />
                            </Box>
                        </Paper>
                    </Grid>

                    {/* Activity Category Distribution */}
                    <Grid item xs={12} md={6}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                Activities by Category
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Distribution of activities by category
                            </Typography>
                            <Box sx={{ height: 300 }}>
                                <Doughnut data={categoryData} options={chartOptions} />
                            </Box>
                        </Paper>
                    </Grid>

                    {/* Activity Completion Trend */}
                    <Grid item xs={12} md={6}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                Activity Completion Trend
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Your activity completion over time
                            </Typography>
                            <Line data={activityCompletionData} options={chartOptions} />
                        </Paper>
                    </Grid>

                    {/* Activity Duration */}
                    <Grid item xs={12} md={6}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                Activity Duration
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                Time spent on different activities (minutes)
                            </Typography>
                            <Bar data={activityDurationData} options={chartOptions} />
                        </Paper>
                    </Grid>

                    {/* Insights Section */}
                    <Grid item xs={12}>
                        <Paper sx={{ p: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                Insights
                            </Typography>
                            <Box sx={{ mt: 2 }}>
                                <Typography variant="body1" sx={{ mb: 1 }}>
                                    • Your average mood level: <strong>4.1 / 5</strong>
                                </Typography>
                                <Typography variant="body1" sx={{ mb: 1 }}>
                                    • Most frequent emotion: <strong>Joy (35%)</strong>
                                </Typography>
                                <Typography variant="body1" sx={{ mb: 1 }}>
                                    • Most common activity category: <strong>Physical</strong>
                                </Typography>
                                <Typography variant="body1" sx={{ mb: 1 }}>
                                    • Activities completed this week: <strong>6</strong>
                                </Typography>
                                <Typography variant="body1" sx={{ mb: 1 }}>
                                    • Total activity time: <strong>135 minutes</strong>
                                </Typography>
                                <Typography variant="body1" sx={{ mb: 1 }}>
                                    • Highest mood day: <strong>May 12 (4.8)</strong>
                                </Typography>
                            </Box>
                        </Paper>
                    </Grid>
                </Grid>

                {error && (
                    <Box sx={{ mt: 2 }}>
                        <Typography color="error">{error}</Typography>
                    </Box>
                )}
            </motion.div>
        </Container>
    );
};

export default Trends; 