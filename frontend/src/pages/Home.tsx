import React from 'react';
import {
    Box,
    Container,
    Typography,
    Grid,
    Card,
    CardContent,
    Button,
    useTheme,
    Paper,
} from '@mui/material';
import {
    SentimentSatisfied as EmotionIcon,
    FitnessCenter as ActivityIcon,
    TrendingUp as TrendIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const Home: React.FC = () => {
    const theme = useTheme();
    const navigate = useNavigate();

    const features = [
        {
            title: 'Women\'s Emotional Wisdom',
            description: 'Analyze your emotions through a feminine lens and receive insights that honor women\'s unique emotional experiences',
            icon: <EmotionIcon sx={{ fontSize: 40 }} />,
            path: '/emotions',
        },
        {
            title: 'Self-Care Practices for Women',
            description: 'Discover nurturing activities designed specifically for women\'s emotional and hormonal wellbeing',
            icon: <ActivityIcon sx={{ fontSize: 40 }} />,
            path: '/activities',
        },
        {
            title: 'Women\'s Emotional Journey',
            description: 'Track your emotional patterns in relation to your cycle, life events, and personal growth as a woman',
            icon: <TrendIcon sx={{ fontSize: 40 }} />,
            path: '/trends',
        },
    ];

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.2,
            },
        },
    };

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: {
                duration: 0.5,
            },
        },
    };

    return (
        <Box
            sx={{
                minHeight: '100vh',
                background: `linear-gradient(135deg, #FFFFFF 0%, #FFE0EB 60%, #FF6B98 100%)`,
                py: 8,
                fontFamily: '"Montserrat", sans-serif',
            }}
        >
            <Container maxWidth="lg">
                <motion.div
                    initial="hidden"
                    animate="visible"
                    variants={containerVariants}
                >
                    <Box
                        component={motion.div}
                        variants={itemVariants}
                        sx={{
                            textAlign: 'center',
                            mb: 8,
                            color: 'white',
                        }}
                    >
                        <Typography
                            variant="h2"
                            component="h1"
                            gutterBottom
                            sx={{
                                fontWeight: 800,
                                textShadow: '0 2px 10px rgba(0,0,0,0.1)',
                                letterSpacing: '-0.02em',
                                fontSize: { xs: '2rem', sm: '2.5rem', md: '3rem' },
                                mb: 3
                            }}
                        >
                            Women's Emotional Wellness Sanctuary
                        </Typography>
                        <Typography
                            variant="h5"
                            sx={{
                                maxWidth: '800px',
                                mx: 'auto',
                                mb: 4,
                                opacity: 0.9,
                                fontFamily: '"Montserrat", sans-serif',
                                fontWeight: 500,
                                lineHeight: 1.6,
                                fontSize: { xs: '1rem', sm: '1.1rem', md: '1.25rem' },
                            }}
                        >
                            Your personal AI companion designed specifically for women's emotional well-being,
                            honoring your unique experiences and nurturing your feminine wisdom
                        </Typography>
                    </Box>

                    <Grid container spacing={4}>
                        {features.map((feature, index) => (
                            <Grid item xs={12} md={4} key={feature.title}>
                                <motion.div variants={itemVariants}>
                                    <Card
                                        component={Paper}
                                        elevation={3}
                                        sx={{
                                            height: '100%',
                                            display: 'flex',
                                            flexDirection: 'column',
                                            transition: 'all 0.3s ease',
                                            borderRadius: 3,
                                            overflow: 'hidden',
                                            border: 'none',
                                            boxShadow: '0 10px 30px rgba(0, 0, 0, 0.08)',
                                            '&:hover': {
                                                transform: 'translateY(-12px)',
                                                boxShadow: '0 16px 40px rgba(0, 0, 0, 0.12)',
                                            },
                                        }}
                                    >
                                        <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 4, backgroundColor: '#FFFFFF' }}>
                                            <Box
                                                sx={{
                                                    color: '#FFFFFF',
                                                    mb: 3,
                                                    background: 'linear-gradient(135deg, #FF6B98 0%, #D84275 100%)',
                                                    width: '90px',
                                                    height: '90px',
                                                    borderRadius: '50%',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    margin: '0 auto 24px',
                                                    boxShadow: '0 8px 20px rgba(255, 107, 152, 0.25)',
                                                    transform: 'rotate(-5deg)',
                                                    transition: 'all 0.3s ease',
                                                    '&:hover': {
                                                        transform: 'rotate(0deg) scale(1.05)',
                                                    }
                                                }}
                                            >
                                                {feature.icon}
                                            </Box>
                                            <Typography
                                                variant="h5"
                                                component="h2"
                                                gutterBottom
                                                sx={{
                                                    fontWeight: 700,
                                                    color: '#2A2A2A',
                                                    fontFamily: '"Montserrat", sans-serif',
                                                    mb: 2,
                                                    fontSize: '1.35rem',
                                                    letterSpacing: '-0.01em'
                                                }}
                                            >
                                                {feature.title}
                                            </Typography>
                                            <Typography
                                                variant="body1"
                                                color="#6E6E6E"
                                                paragraph
                                                sx={{
                                                    fontSize: '1rem',
                                                    lineHeight: 1.7,
                                                    mb: 3,
                                                    fontWeight: 400
                                                }}
                                            >
                                                {feature.description}
                                            </Typography>
                                            <Button
                                                variant="contained"
                                                onClick={() => navigate(feature.path)}
                                                sx={{
                                                    mt: 2,
                                                    background: 'linear-gradient(90deg, #FF6B98 0%, #D84275 100%)',
                                                    color: 'white',
                                                    borderRadius: 8,
                                                    padding: '10px 28px',
                                                    textTransform: 'none',
                                                    fontWeight: 600,
                                                    boxShadow: '0 4px 12px rgba(255, 107, 152, 0.25)',
                                                    transition: 'all 0.3s ease',
                                                    '&:hover': {
                                                        boxShadow: '0 6px 16px rgba(255, 107, 152, 0.35)',
                                                        transform: 'translateY(-2px)',
                                                        background: 'linear-gradient(90deg, #FF6B98 20%, #D84275 100%)',
                                                    }
                                                }}
                                            >
                                                Explore
                                            </Button>
                                        </CardContent>
                                    </Card>
                                </motion.div>
                            </Grid>
                        ))}
                    </Grid>

                    <Box
                        component={motion.div}
                        variants={itemVariants}
                        sx={{
                            textAlign: 'center',
                            mt: 8,
                            color: 'white',
                        }}
                    >
                        <Typography
                            variant="h4"
                            gutterBottom
                            sx={{
                                fontFamily: '"Montserrat", sans-serif',
                                fontWeight: 700,
                                mb: 2,
                                letterSpacing: '-0.01em'
                            }}
                        >
                            Ready to Begin Your Women's Wellness Journey?
                        </Typography>
                        <Typography
                            variant="body1"
                            sx={{
                                mb: 5,
                                opacity: 0.9,
                                maxWidth: '700px',
                                mx: 'auto',
                                fontSize: '1.15rem',
                                lineHeight: 1.7,
                                fontWeight: 500
                            }}
                        >
                            Embrace your feminine wisdom by exploring your emotions or discovering
                            nurturing activities designed specifically for women's unique needs
                        </Typography>
                        <Button
                            variant="contained"
                            size="large"
                            onClick={() => navigate('/emotions')}
                            sx={{
                                px: 6,
                                py: 2,
                                borderRadius: 8,
                                textTransform: 'none',
                                fontSize: '1.2rem',
                                fontWeight: 600,
                                background: 'linear-gradient(90deg, #7E57C2 0%, #4D2C91 100%)',
                                boxShadow: '0 8px 24px rgba(126, 87, 194, 0.4)',
                                transition: 'all 0.3s ease',
                                '&:hover': {
                                    boxShadow: '0 12px 28px rgba(126, 87, 194, 0.5)',
                                    transform: 'translateY(-3px)',
                                }
                            }}
                        >
                            Begin Your Feminine Journey
                        </Button>
                    </Box>
                </motion.div>
            </Container>
        </Box>
    );
};

export default Home; 