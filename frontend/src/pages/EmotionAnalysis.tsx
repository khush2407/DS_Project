import React, { useState } from 'react';
import {
    Box,
    Card,
    CardContent,
    TextField,
    Button,
    Typography,
    CircularProgress,
    Grid,
    Chip,
    useTheme,
    Paper,
    LinearProgress,
} from '@mui/material';
import { analyzeEmotion, getRecommendations } from '../services/api';
import { EmotionResponse, RecommendationResponse, Activity } from '../types';
import { useApp } from '../context/AppContext';

const EmotionAnalysis: React.FC = () => {
    const [text, setText] = useState('');
    const [emotionData, setEmotionData] = useState<EmotionResponse | null>(null);
    const [recommendations, setRecommendations] = useState<Activity[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const theme = useTheme();
    const { sessionId } = useApp();

    const handleAnalyze = async () => {
        if (!text.trim()) return;

        setLoading(true);
        setError(null);

        try {
            // Use the session ID from context if available, otherwise use 'current-session'
            const currentSessionId = sessionId || 'current-session';
            
            const result = await analyzeEmotion(text, currentSessionId);
            setEmotionData(result);
            setError(null);

            // Get recommendations based on the emotion analysis result
            const recommendationResult = await getRecommendations(result, currentSessionId);
            setRecommendations(recommendationResult.activities || []);
        } catch (err) {
            console.error('Error analyzing emotions:', err);
            setError('Failed to analyze emotions. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box sx={{ p: 4, backgroundColor: '#FAFAFA' }}>
            <Typography
                variant="h4"
                gutterBottom
                sx={{
                    color: '#2A2A2A',
                    fontWeight: 700,
                    fontFamily: '"Montserrat", sans-serif',
                    letterSpacing: '-0.01em',
                    mb: 2
                }}
            >
                Women's Emotional Wellness Journey
            </Typography>
            <Typography
                variant="body1"
                paragraph
                sx={{
                    fontSize: '1.1rem',
                    lineHeight: 1.7,
                    color: '#6E6E6E',
                    maxWidth: '900px',
                    mb: 4
                }}
            >
                As women, we navigate a complex emotional landscape shaped by unique biological, social, and cultural experiences.
                Our emotions are valid and powerful. Share how you're feeling in this safe space, and we'll analyze your emotions
                to provide personalized wellness recommendations designed specifically for women's needs and strengths.
            </Typography>

            <Paper
                elevation={2}
                sx={{
                    p: 4,
                    mb: 5,
                    borderRadius: 3,
                    boxShadow: '0 8px 30px rgba(0, 0, 0, 0.06)',
                    border: 'none',
                    backgroundColor: '#FFFFFF'
                }}
            >
                <Typography
                    variant="h5"
                    sx={{
                        mb: 2,
                        color: '#FF6B98',
                        fontFamily: '"Montserrat", sans-serif',
                        fontWeight: 600,
                        letterSpacing: '-0.01em'
                    }}
                >
                    Express Yourself in Our Women's Safe Space
                </Typography>
                
                <Typography
                    variant="body2"
                    sx={{
                        mb: 3,
                        color: '#6E6E6E',
                        fontSize: '1rem',
                        lineHeight: 1.6
                    }}
                >
                    As women, we often hold back our true feelings. Here, you can express yourself authentically without judgment.
                    Your emotional experiences are valid and deserve to be heard.
                </Typography>
                
                <TextField
                    fullWidth
                    multiline
                    rows={5}
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="How are you feeling today? What challenges are you facing as a woman? What's bringing you joy or concern? Share as much or as little as feels comfortable..."
                    variant="outlined"
                    sx={{
                        mb: 4,
                        '& .MuiOutlinedInput-root': {
                            borderRadius: 2,
                            backgroundColor: '#FFFFFF',
                            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.06)',
                            },
                            '&.Mui-focused': {
                                boxShadow: '0 4px 12px rgba(255, 107, 152, 0.15)',
                                '& fieldset': {
                                    borderColor: '#FF6B98',
                                    borderWidth: 2,
                                },
                            },
                        },
                        '& .MuiInputBase-input': {
                            lineHeight: 1.7,
                            padding: '16px',
                            fontSize: '1rem',
                        }
                    }}
                />

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography
                        variant="body2"
                        sx={{
                            color: '#6E6E6E',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1
                        }}
                    >
                        <Box
                            component="span"
                            sx={{
                                width: 8,
                                height: 8,
                                borderRadius: '50%',
                                backgroundColor: '#4CAF50',
                                display: 'inline-block'
                            }}
                        />
                        Your thoughts are private and secure
                    </Typography>
                    
                    <Button
                        variant="contained"
                        onClick={handleAnalyze}
                        disabled={loading || !text.trim()}
                        sx={{
                            background: 'linear-gradient(90deg, #FF6B98 0%, #D84275 100%)',
                            borderRadius: 8,
                            padding: '12px 28px',
                            fontWeight: 600,
                            boxShadow: '0 4px 12px rgba(255, 107, 152, 0.25)',
                            transition: 'all 0.3s ease',
                            '&:hover': {
                                boxShadow: '0 6px 16px rgba(255, 107, 152, 0.35)',
                                transform: 'translateY(-2px)',
                            },
                            '&:disabled': {
                                background: 'linear-gradient(90deg, #E0E0E0 0%, #BDBDBD 100%)',
                                boxShadow: 'none',
                            }
                        }}
                    >
                        {loading ? <CircularProgress size={24} color="inherit" /> : 'Analyze My Feelings'}
                    </Button>
                </Box>
            </Paper>

            {error && (
                <Typography color="error" sx={{ mb: 2 }}>
                    {error}
                </Typography>
            )}

            {emotionData && (
                <Paper
                    elevation={2}
                    sx={{
                        p: 4,
                        mb: 5,
                        borderRadius: 3,
                        boxShadow: '0 8px 30px rgba(0, 0, 0, 0.06)',
                        border: 'none',
                        backgroundColor: '#FFFFFF'
                    }}
                >
                    <Typography
                        variant="h5"
                        gutterBottom
                        sx={{
                            color: '#2A2A2A',
                            fontFamily: '"Montserrat", sans-serif',
                            fontWeight: 700,
                            letterSpacing: '-0.01em',
                            mb: 3
                        }}
                    >
                        Your Feminine Emotional Wisdom
                    </Typography>
                    
                    <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, alignItems: { xs: 'flex-start', sm: 'center' }, mb: 3, gap: 2 }}>
                        <Typography
                            variant="h6"
                            sx={{
                                color: '#6E6E6E',
                                fontWeight: 600,
                                fontSize: '1.1rem'
                            }}
                        >
                            Primary Emotion:
                        </Typography>
                        <Chip
                            label={emotionData.primary_emotion.toUpperCase()}
                            sx={{
                                background: 'linear-gradient(90deg, #FF6B98 0%, #D84275 100%)',
                                color: '#FFFFFF',
                                fontWeight: 600,
                                fontSize: '1rem',
                                padding: '24px 12px',
                                borderRadius: 6,
                                boxShadow: '0 4px 12px rgba(255, 107, 152, 0.2)',
                            }}
                        />
                    </Box>
                    
                    <Typography
                        variant="body1"
                        sx={{
                            mb: 4,
                            lineHeight: 1.7,
                            fontSize: '1.05rem',
                            color: '#2A2A2A',
                            backgroundColor: '#F5F5F5',
                            p: 3,
                            borderRadius: 2
                        }}
                    >
                        <Box component="span" sx={{ fontWeight: 600 }}>What This Means For You:</Box> {emotionData.summary}
                    </Typography>
                    
                    <Box
                        sx={{
                            background: 'linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%)',
                            p: 3,
                            borderRadius: 2,
                            mb: 4,
                            boxShadow: '0 4px 12px rgba(126, 87, 194, 0.1)',
                        }}
                    >
                        <Typography
                            variant="body1"
                            sx={{
                                color: '#4D2C91',
                                lineHeight: 1.7,
                                fontSize: '1rem'
                            }}
                        >
                            As women, we possess unique emotional intelligence that has historically been undervalued.
                            Our emotions are not weaknesses but sources of insight and strength.
                            Acknowledging your feelings is a powerful act of self-care and feminine wisdom.
                        </Typography>
                    </Box>
                    
                    <Typography
                        variant="h6"
                        sx={{
                            color: '#2A2A2A',
                            fontWeight: 600,
                            mb: 2,
                            fontSize: '1.1rem'
                        }}
                    >
                        Your Emotional Spectrum:
                    </Typography>
                    
                    <Grid container spacing={2}>
                        {Object.entries(emotionData.emotions)
                            .sort(([, a], [, b]) => b - a)
                            .slice(0, 5)
                            .map(([emotion, intensity]) => (
                                <Grid item xs={12} sm={6} md={4} key={emotion}>
                                    <Box sx={{
                                        display: 'flex',
                                        flexDirection: 'column',
                                        backgroundColor: '#F5F5F5',
                                        p: 2,
                                        borderRadius: 2,
                                        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
                                        height: '100%'
                                    }}>
                                        <Typography
                                            sx={{
                                                mb: 1.5,
                                                fontWeight: 600,
                                                color: '#2A2A2A',
                                                fontSize: '0.95rem',
                                                textTransform: 'capitalize'
                                            }}
                                        >
                                            {emotion}
                                        </Typography>
                                        <Box>
                                            <LinearProgress
                                                variant="determinate"
                                                value={intensity * 100}
                                                sx={{
                                                    height: 8,
                                                    borderRadius: 4,
                                                    backgroundColor: '#E0E0E0',
                                                    '& .MuiLinearProgress-bar': {
                                                        background: 'linear-gradient(90deg, #FF6B98 0%, #D84275 100%)',
                                                        borderRadius: 4,
                                                    }
                                                }}
                                            />
                                        </Box>
                                        <Typography
                                            variant="body2"
                                            sx={{
                                                color: '#6E6E6E',
                                                fontWeight: 600,
                                                fontSize: '0.9rem',
                                                alignSelf: 'flex-end'
                                            }}
                                        >
                                            {(intensity * 100).toFixed(0)}%
                                        </Typography>
                                    </Box>
                                </Grid>
                            ))}
                    </Grid>
                </Paper>
            )}

            {recommendations.length > 0 && (
                <Paper
                    elevation={2}
                    sx={{
                        p: 4,
                        borderRadius: 3,
                        boxShadow: '0 8px 30px rgba(0, 0, 0, 0.06)',
                        border: 'none',
                        backgroundColor: '#FFFFFF'
                    }}
                >
                    <Typography
                        variant="h5"
                        gutterBottom
                        sx={{
                            color: '#2A2A2A',
                            fontFamily: '"Montserrat", sans-serif',
                            fontWeight: 700,
                            letterSpacing: '-0.01em',
                            mb: 2
                        }}
                    >
                        Women's Wellness Recommendations
                    </Typography>
                    <Typography
                        variant="body1"
                        sx={{
                            mb: 4,
                            lineHeight: 1.7,
                            color: '#6E6E6E',
                            fontSize: '1.05rem'
                        }}
                    >
                        These activities are specifically designed for women by women, honoring our unique emotional experiences,
                        hormonal fluctuations, and the social pressures we navigate. Each practice supports your emotional well-being
                        through a feminine-centered approach to wellness.
                    </Typography>
                    {recommendations.map((activity) => (
                        <Box
                            key={activity.id}
                            sx={{
                                mb: 4,
                                p: 3,
                                backgroundColor: '#FFFFFF',
                                borderRadius: 3,
                                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)',
                                border: '1px solid #F5F5F5',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                    boxShadow: '0 8px 30px rgba(0, 0, 0, 0.1)',
                                    transform: 'translateY(-4px)',
                                }
                            }}
                        >
                            <Typography
                                variant="h6"
                                sx={{
                                    color: '#FF6B98',
                                    fontWeight: 700,
                                    mb: 2,
                                    fontSize: '1.2rem'
                                }}
                            >
                                {activity.title}
                            </Typography>
                            <Typography
                                variant="body1"
                                sx={{
                                    mb: 3,
                                    color: '#2A2A2A',
                                    lineHeight: 1.7
                                }}
                            >
                                {activity.description}
                            </Typography>
                            <Box
                                sx={{
                                    mb: 3,
                                    p: 2,
                                    backgroundColor: '#F3E5F5',
                                    borderRadius: 2,
                                    borderLeft: '4px solid #7E57C2'
                                }}
                            >
                                <Typography
                                    variant="body2"
                                    sx={{
                                        color: '#4D2C91',
                                        lineHeight: 1.6
                                    }}
                                >
                                    {activity.emotional_context || "This practice honors women's intuitive wisdom and supports emotional balance in a way that respects our unique biological and social experiences."}
                                </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                                {activity.benefits && activity.benefits.map((benefit, index) => (
                                    <Chip
                                        key={index}
                                        label={benefit}
                                        size="medium"
                                        sx={{
                                            backgroundColor: '#FFE0EB',
                                            color: '#D84275',
                                            fontWeight: 500,
                                            borderRadius: 6,
                                            padding: '4px',
                                            '&:hover': {
                                                backgroundColor: '#FFD0E0',
                                                transform: 'translateY(-2px)'
                                            },
                                            transition: 'all 0.2s ease'
                                        }}
                                    />
                                ))}
                            </Box>
                            <Typography
                                variant="subtitle2"
                                sx={{
                                    color: '#6E6E6E',
                                    fontWeight: 600,
                                    display: 'inline-block',
                                    backgroundColor: '#F5F5F5',
                                    px: 2,
                                    py: 0.5,
                                    borderRadius: 6
                                }}
                            >
                                Duration: {activity.duration}
                            </Typography>
                        </Box>
                    ))}
                </Paper>
            )}
        </Box>
    );
};

export default EmotionAnalysis; 