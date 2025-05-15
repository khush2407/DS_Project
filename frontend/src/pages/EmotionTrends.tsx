import React, { useState } from 'react';
import {
    Box,
    Container,
    Typography,
    Paper,
    Grid,
    Card,
    CardContent,
    useTheme,
    Button,
    Rating,
} from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { useApp } from '../context/AppContext';
import { Mood as MoodIcon } from '@mui/icons-material';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const EmotionTrends: React.FC = () => {
    const theme = useTheme();
    const { activityHistory } = useApp();
    const [currentMood, setCurrentMood] = useState<number | null>(null);

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
        });
    };

    const moodData = {
        labels: activityHistory.map(item => formatDate(item.start_time)),
        datasets: [
            {
                label: 'Mood Level',
                data: activityHistory.map(item => item.mood_level || 0),
                borderColor: theme.palette.primary.main,
                backgroundColor: theme.palette.primary.light,
                tension: 0.4,
            },
        ],
    };

    const activityCompletionData = {
        labels: activityHistory.map(item => formatDate(item.start_time)),
        datasets: [
            {
                label: 'Activities Completed',
                data: activityHistory.map(item => item.completed ? 1 : 0),
                borderColor: theme.palette.success.main,
                backgroundColor: theme.palette.success.light,
                tension: 0.4,
            },
        ],
    };

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top' as const,
            },
            title: {
                display: true,
                text: 'Your Wellness Journey',
            },
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 5,
            },
        },
    };

    const handleMoodSubmit = () => {
        if (currentMood !== null) {
            // Here you would typically save the mood to your backend
            console.log('Mood submitted:', currentMood);
            setCurrentMood(null);
        }
    };

    return (
        <Container maxWidth="lg" sx={{ py: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom>
                Emotion Trends
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
                Track your emotional well-being and activity patterns
            </Typography>

            <Grid container spacing={4}>
                <Grid item xs={12}>
                    <Paper sx={{ p: 3, mb: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            How are you feeling today?
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                            <Rating
                                value={currentMood}
                                onChange={(_, value) => setCurrentMood(value)}
                                max={5}
                                icon={<MoodIcon fontSize="large" />}
                                emptyIcon={<MoodIcon fontSize="large" />}
                            />
                            <Button
                                variant="contained"
                                onClick={handleMoodSubmit}
                                disabled={currentMood === null}
                            >
                                Save Mood
                            </Button>
                        </Box>
                    </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Mood Trends
                        </Typography>
                        <Box sx={{ height: 300 }}>
                            <Line data={moodData} options={chartOptions} />
                        </Box>
                    </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            Activity Completion
                        </Typography>
                        <Box sx={{ height: 300 }}>
                            <Line data={activityCompletionData} options={chartOptions} />
                        </Box>
                    </Paper>
                </Grid>

                <Grid item xs={12}>
                    <Card>
                        <CardContent>
                            <Typography variant="h6" gutterBottom>
                                Insights
                            </Typography>
                            <Typography variant="body1" paragraph>
                                • Average mood level: {
                                    activityHistory.length > 0 ?
                                        (activityHistory.reduce((acc, curr) => acc + (curr.mood_level || 0), 0) / 
                                        activityHistory.length).toFixed(1) : 'No data'
                                    } / 5
                            </Typography>
                            <Typography variant="body1">
                                • Activities completed: {
                                    activityHistory.filter(item => item.completed).length
                                } out of {activityHistory.length}
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>
        </Container>
    );
};

export default EmotionTrends; 