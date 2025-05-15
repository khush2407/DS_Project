import React from 'react';
import {
    Box,
    Typography,
    Card,
    CardContent,
    Chip,
    LinearProgress,
    useTheme,
} from '@mui/material';
import {
    Timer,
    CheckCircle,
    Schedule,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { ActivityHistoryItem } from '../types';

interface ActivityHistoryProps {
    history: ActivityHistoryItem[];
}

const ActivityHistory: React.FC<ActivityHistoryProps> = ({ history }) => {
    const theme = useTheme();

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const formatDuration = (minutes: number) => {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        if (hours > 0) {
            return `${hours}h ${mins}m`;
        }
        return `${mins}m`;
    };

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1,
            },
        },
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0 },
    };

    return (
        <Box>
            <motion.div
                variants={containerVariants}
                initial="hidden"
                animate="visible"
            >
                {history.length === 0 ? (
                    <Box
                        sx={{
                            textAlign: 'center',
                            py: 8,
                            color: 'text.secondary',
                        }}
                    >
                        <Typography variant="h6" gutterBottom>
                            No activity history yet
                        </Typography>
                        <Typography variant="body2">
                            Start an activity to begin tracking your progress
                        </Typography>
                    </Box>
                ) : (
                    history.map((item) => (
                        <motion.div
                            key={item.id}
                            variants={itemVariants}
                            style={{ marginBottom: theme.spacing(2) }}
                        >
                            <Card
                                sx={{
                                    transition: 'transform 0.2s',
                                    '&:hover': {
                                        transform: 'translateY(-4px)',
                                    },
                                }}
                            >
                                <CardContent>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                                        <Box>
                                            <Typography variant="h6" gutterBottom>
                                                {item.activity_title}
                                            </Typography>
                                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                                <Chip
                                                    icon={<Schedule />}
                                                    label={formatDate(item.start_time)}
                                                    size="small"
                                                    variant="outlined"
                                                />
                                                {item.completed && (
                                                    <Chip
                                                        icon={<CheckCircle />}
                                                        label={`Completed in ${Math.round(item.duration / 60)} minutes`}
                                                        color="success"
                                                        size="small"
                                                        variant="outlined"
                                                    />
                                                )}
                                            </Box>
                                        </Box>
                                    </Box>

                                    {!item.completed && (
                                        <Box sx={{ mt: 2 }}>
                                            <Typography variant="body2" color="text.secondary" gutterBottom>
                                                Progress: {Math.round(item.progress * 100)}%
                                            </Typography>
                                            <LinearProgress
                                                variant="determinate"
                                                value={item.progress * 100}
                                                sx={{
                                                    height: 8,
                                                    borderRadius: 4,
                                                    backgroundColor: theme.palette.grey[200],
                                                    '& .MuiLinearProgress-bar': {
                                                        borderRadius: 4,
                                                    },
                                                }}
                                            />
                                        </Box>
                                    )}
                                </CardContent>
                            </Card>
                        </motion.div>
                    ))
                )}
            </motion.div>
        </Box>
    );
};

export default ActivityHistory; 