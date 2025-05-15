import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Button,
    Grid,
    Chip,
    TextField,
    CircularProgress,
    Alert,
    Snackbar,
    Container,
    Paper,
    Switch,
    FormControlLabel,
} from '@mui/material';
import { getActivityPreferences, updatePreferences } from '../services/api';
import { UserPreferences } from '../types';

const Settings: React.FC = () => {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [preferences, setPreferences] = useState<UserPreferences>({
        difficulty_level: 'beginner',
        preferred_duration: 'short',
        favorite_activities: [],
        categories: [],
        notifications: true
    });
    const [newActivity, setNewActivity] = useState('');
    const [notification, setNotification] = useState({
        open: false,
        message: '',
        severity: 'success' as 'success' | 'error'
    });

    useEffect(() => {
        loadPreferences();
    }, []);

    const loadPreferences = async () => {
        try {
            setLoading(true);
            const data = await getActivityPreferences('current-session');
            setPreferences(data);
        } catch (error) {
            console.error('Error loading preferences:', error);
            setNotification({
                open: true,
                message: 'Failed to load preferences',
                severity: 'error'
            });
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        try {
            setSaving(true);
            await updatePreferences('current-session', preferences);
            setNotification({
                open: true,
                message: 'Preferences saved successfully',
                severity: 'success'
            });
        } catch (error) {
            console.error('Error saving preferences:', error);
            setNotification({
                open: true,
                message: 'Failed to save preferences',
                severity: 'error'
            });
        } finally {
            setSaving(false);
        }
    };

    const handleAddActivity = () => {
        if (newActivity.trim()) {
            setPreferences(prev => ({
                ...prev,
                favorite_activities: [...prev.favorite_activities, newActivity.trim()]
            }));
            setNewActivity('');
        }
    };

    const handleRemoveActivity = (activity: string) => {
        setPreferences(prev => ({
            ...prev,
            favorite_activities: prev.favorite_activities.filter(a => a !== activity)
        }));
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Container maxWidth="md" sx={{ py: 4 }}>
            <Paper sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom>
                    Settings
                </Typography>
                <Typography variant="body1" color="text.secondary" paragraph>
                    Customize your wellness experience by adjusting your preferences.
                </Typography>

                <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                        <FormControl fullWidth>
                            <InputLabel>Difficulty Level</InputLabel>
                            <Select
                                value={preferences.difficulty_level}
                                label="Difficulty Level"
                                onChange={(e) =>
                                    setPreferences(prev => ({ ...prev, difficulty_level: e.target.value }))
                                }
                            >
                                <MenuItem value="beginner">Beginner</MenuItem>
                                <MenuItem value="intermediate">Intermediate</MenuItem>
                                <MenuItem value="advanced">Advanced</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <FormControl fullWidth>
                            <InputLabel>Preferred Duration</InputLabel>
                            <Select
                                value={preferences.preferred_duration}
                                label="Preferred Duration"
                                onChange={(e) =>
                                    setPreferences(prev => ({ ...prev, preferred_duration: e.target.value }))
                                }
                            >
                                <MenuItem value="short">Short (5-15 minutes)</MenuItem>
                                <MenuItem value="medium">Medium (15-30 minutes)</MenuItem>
                                <MenuItem value="long">Long (30+ minutes)</MenuItem>
                            </Select>
                        </FormControl>
                    </Grid>

                    <Grid item xs={12}>
                        <Box sx={{ mb: 2 }}>
                            <Typography variant="h6" gutterBottom>
                                Favorite Activities
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                                <TextField
                                    fullWidth
                                    label="Add Activity"
                                    value={newActivity}
                                    onChange={(e) => setNewActivity(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleAddActivity()}
                                />
                                <Button
                                    variant="contained"
                                    onClick={handleAddActivity}
                                    disabled={!newActivity.trim()}
                                >
                                    Add
                                </Button>
                            </Box>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                {preferences.favorite_activities.map((activity: string) => (
                                    <Chip
                                        key={activity}
                                        label={activity}
                                        onDelete={() => handleRemoveActivity(activity)}
                                    />
                                ))}
                            </Box>
                        </Box>
                    </Grid>

                    <Grid item xs={12}>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={preferences.notifications}
                                    onChange={(e) => setPreferences(prev => ({ ...prev, notifications: e.target.checked }))}
                                />
                            }
                            label="Enable Notifications"
                        />
                    </Grid>
                </Grid>

                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                        variant="contained"
                        color="primary"
                        onClick={handleSave}
                        disabled={saving}
                    >
                        {saving ? <CircularProgress size={24} /> : 'Save Preferences'}
                    </Button>
                </Box>
            </Paper>

            <Snackbar
                open={notification.open}
                autoHideDuration={6000}
                onClose={() => setNotification((prev) => ({ ...prev, open: false }))}
            >
                <Alert
                    onClose={() => setNotification((prev) => ({ ...prev, open: false }))}
                    severity={notification.severity}
                    sx={{ width: '100%' }}
                >
                    {notification.message}
                </Alert>
            </Snackbar>
        </Container>
    );
};

export default Settings; 