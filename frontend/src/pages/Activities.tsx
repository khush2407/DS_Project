import React, { useEffect, useState } from 'react';
import {
    Container,
    Box,
    Typography,
    Tabs,
    Tab,
    Snackbar,
    Alert,
    useTheme,
    CircularProgress,
    Button,
    Rating,
} from '@mui/material';
import { motion } from 'framer-motion';
import ActivityGrid from '../components/ActivityGrid';
import ActivityDialog from '../components/ActivityDialog';
import ActivityHistory from '../components/ActivityHistory';
import { Activity, ActivityHistoryItem } from '../types';
import { Mood as MoodIcon } from '@mui/icons-material';
import {
    getRecommendations,
    toggleFavorite,
    shareActivity,
    startActivity,
    completeActivity,
    updateProgress,
} from '../api/activities';

const Activities: React.FC = () => {
    const theme = useTheme();
    const [activities, setActivities] = useState<Activity[]>([]);
    const [history, setHistory] = useState<ActivityHistoryItem[]>([]);
    const [favorites, setFavorites] = useState<string[]>([]);
    const [progress, setProgress] = useState<Record<string, number>>({});
    const [selectedTab, setSelectedTab] = useState(0);
    const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeActivityId, setActiveActivityId] = useState<string | null>(null);
    const [currentMood, setCurrentMood] = useState<number | null>(null);

    useEffect(() => {
        fetchActivities();
    }, []);

    const fetchActivities = async () => {
        try {
            setLoading(true);
            const data = await getRecommendations();
            setActivities(data.activities);
            setFavorites(data.favorites);
            setProgress(data.progress);
            setHistory(data.history);
        } catch (err) {
            setError('Failed to fetch activities');
        } finally {
            setLoading(false);
        }
    };

    const handleStartActivity = (activity: Activity) => {
        setSelectedActivity(activity);
        setDialogOpen(true);
    };

    const handleActivityStart = async () => {
        if (!selectedActivity) return;
        
        try {
            await startActivity(selectedActivity.id);
            setActiveActivityId(selectedActivity.id);
            setDialogOpen(false);
            setSelectedActivity(null);
            setError('Activity started successfully!');
        } catch (err) {
            setError('Failed to start activity');
        }
    };

    const handleCompleteActivity = async () => {
        if (!activeActivityId || currentMood === null) return;

        try {
            await completeActivity(activeActivityId);
            setActiveActivityId(null);
            setCurrentMood(null);
            await fetchActivities(); // Refresh data
            setError('Activity completed successfully!');
        } catch (err) {
            setError('Failed to complete activity');
        }
    };

    const handleFavorite = async (activityId: string) => {
        try {
            await toggleFavorite(activityId);
            setFavorites(prev =>
                prev.includes(activityId)
                    ? prev.filter(id => id !== activityId)
                    : [...prev, activityId]
            );
        } catch (err) {
            setError('Failed to update favorites');
        }
    };

    const handleShare = async (activity: Activity) => {
        try {
            const shareUrl = await shareActivity(activity.id);
            await navigator.clipboard.writeText(shareUrl);
            setError('Share link copied to clipboard!');
        } catch (err) {
            setError('Failed to share activity');
        }
    };

    const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
        setSelectedTab(newValue);
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

    return (
        <Container maxWidth="lg" sx={{ py: 5, backgroundColor: '#fff0f5', borderRadius: 4, boxShadow: '0 4px 20px rgba(216, 79, 139, 0.1)' }}>
            <motion.div
                variants={pageVariants}
                initial="hidden"
                animate="visible"
            >
                <Box sx={{ mb: 5 }}>
                    <Typography
                        variant="h4"
                        component="h1"
                        gutterBottom
                        sx={{
                            color: '#ad1457',
                            fontFamily: '"Playfair Display", serif',
                            fontWeight: 'bold'
                        }}
                    >
                        Women's Self-Care Practices
                    </Typography>
                    <Typography
                        variant="body1"
                        sx={{
                            color: '#6a1b9a',
                            fontSize: '1.1rem',
                            maxWidth: '800px',
                            lineHeight: 1.6
                        }}
                    >
                        Discover nurturing activities designed specifically for women's unique emotional needs,
                        hormonal balance, and feminine energy. These practices honor your intuitive wisdom and
                        support your journey as a woman.
                    </Typography>
                </Box>

                {activeActivityId && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                    >
                        <Box
                            sx={{
                                mb: 5,
                                p: 4,
                                borderRadius: 3,
                                bgcolor: '#fce4ec',
                                color: '#880e4f',
                                border: '1px solid #f8bbd0',
                                boxShadow: '0 4px 15px rgba(216, 79, 139, 0.15)',
                            }}
                        >
                            <Typography
                                variant="h6"
                                gutterBottom
                                sx={{
                                    fontFamily: '"Playfair Display", serif',
                                    fontWeight: 'bold',
                                    color: '#ad1457'
                                }}
                            >
                                Your Current Self-Care Practice: {activities.find(a => a.id === activeActivityId)?.title}
                            </Typography>
                            <Typography variant="body2" sx={{ mb: 3, fontStyle: 'italic', color: '#6a1b9a' }}>
                                Taking time for yourself is an act of self-love. How is this practice affecting your feminine energy?
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
                                <Typography
                                    variant="body1"
                                    sx={{
                                        mr: 2,
                                        fontWeight: 'medium',
                                        color: '#ad1457'
                                    }}
                                >
                                    How are you feeling now?
                                </Typography>
                                <Rating
                                    value={currentMood}
                                    onChange={(_, value) => setCurrentMood(value)}
                                    max={5}
                                    icon={<MoodIcon fontSize="large" sx={{ color: '#d84f8b' }} />}
                                    emptyIcon={<MoodIcon fontSize="large" sx={{ color: '#f8bbd0' }} />}
                                />
                                <Box sx={{ flexGrow: 1 }} />
                                <Button
                                    variant="contained"
                                    onClick={handleCompleteActivity}
                                    disabled={currentMood === null}
                                    sx={{
                                        backgroundColor: '#d84f8b',
                                        borderRadius: 28,
                                        padding: '10px 24px',
                                        textTransform: 'none',
                                        fontWeight: 'bold',
                                        boxShadow: '0 4px 12px rgba(216, 79, 139, 0.3)',
                                        '&:hover': {
                                            backgroundColor: '#c2185b',
                                        },
                                        '&.Mui-disabled': {
                                            backgroundColor: '#f8bbd0',
                                            color: '#880e4f',
                                        }
                                    }}
                                >
                                    Complete Your Practice
                                </Button>
                            </Box>
                        </Box>
                    </motion.div>
                )}

                <Box sx={{
                    borderBottom: 1,
                    borderColor: '#f8bbd0',
                    mb: 4,
                    mt: 2
                }}>
                    <Tabs
                        value={selectedTab}
                        onChange={handleTabChange}
                        aria-label="activity tabs"
                        sx={{
                            '& .MuiTabs-indicator': {
                                backgroundColor: '#d84f8b',
                                height: 3,
                            },
                            '& .MuiTab-root': {
                                fontWeight: 'bold',
                                fontSize: '1rem',
                                color: '#ad1457',
                                '&.Mui-selected': {
                                    color: '#880e4f',
                                }
                            }
                        }}
                    >
                        <Tab label="Self-Care Practices" />
                        <Tab label="Your Journey" />
                    </Tabs>
                </Box>

                <motion.div
                    key={selectedTab === 0 ? "activities" : "history"}
                    initial={{ opacity: 0, x: selectedTab === 0 ? 20 : -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: selectedTab === 0 ? -20 : 20 }}
                    transition={{ duration: 0.3 }}
                >
                    {selectedTab === 0 ? (
                        <ActivityGrid
                            activities={activities}
                            onStartActivity={handleStartActivity}
                            onFavoriteActivity={handleFavorite}
                            onShareActivity={handleShare}
                            favoriteActivities={favorites}
                            activityProgress={progress}
                        />
                    ) : (
                        <ActivityHistory history={history} />
                    )}
                </motion.div>

                <ActivityDialog
                    activity={selectedActivity}
                    open={dialogOpen}
                    onClose={() => setDialogOpen(false)}
                    onStart={handleActivityStart}
                    progress={selectedActivity ? progress[selectedActivity.id] : 0}
                />

                <Snackbar
                    open={!!error}
                    autoHideDuration={6000}
                    onClose={() => setError(null)}
                    anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
                >
                    <Alert
                        onClose={() => setError(null)}
                        severity={error?.includes('Failed') ? 'error' : 'success'}
                        sx={{ width: '100%' }}
                    >
                        {error}
                    </Alert>
                </Snackbar>
            </motion.div>
        </Container>
    );
};

export default Activities; 