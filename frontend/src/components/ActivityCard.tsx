import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
  LinearProgress,
  IconButton,
  Tooltip,
  useTheme,
  CardMedia,
  Rating,
  Stack,
} from '@mui/material';
import {
  Favorite,
  FavoriteBorder,
  Share,
  Timer,
  TrendingUp,
  EmojiEmotions,
  Star,
  StarBorder,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { Activity } from '../types';

interface ActivityCardProps {
  activity: Activity;
  onStart: (activity: Activity) => void;
  onFavorite: (activityId: string) => void;
  onShare: (activity: Activity) => void;
  isFavorite?: boolean;
  progress?: number;
}

const ActivityCard: React.FC<ActivityCardProps> = ({
  activity,
  onStart,
  onFavorite,
  onShare,
  isFavorite = false,
  progress = 0,
}) => {
  const theme = useTheme();

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
    hover: { 
      scale: 1.02,
      boxShadow: theme.shadows[8],
      transition: {
        duration: 0.3,
        ease: "easeInOut"
      }
    },
  };

  const chipVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: { opacity: 1, scale: 1 },
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'beginner':
        return theme.palette.success.main;
      case 'intermediate':
        return theme.palette.warning.main;
      case 'advanced':
        return theme.palette.error.main;
      default:
        return theme.palette.primary.main;
    }
  };

  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
      transition={{ duration: 0.3 }}
    >
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'visible',
          borderRadius: 2,
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            transform: 'translateY(-4px)',
          },
        }}
      >
        <CardMedia
          component="div"
          sx={{
            height: 140,
            background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.primary.light} 90%)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
          }}
        >
          <EmojiEmotions sx={{ fontSize: 60 }} />
        </CardMedia>

        <CardContent sx={{ flexGrow: 1, pb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="h6" component="h2" gutterBottom>
              {activity.title}
            </Typography>
            <Box>
              <Tooltip title={isFavorite ? "Remove from favorites" : "Add to favorites"}>
                <IconButton
                  onClick={() => onFavorite(activity.id)}
                  color="primary"
                  size="small"
                  sx={{
                    transition: 'transform 0.2s',
                    '&:hover': {
                      transform: 'scale(1.1)',
                    },
                  }}
                >
                  {isFavorite ? <Favorite /> : <FavoriteBorder />}
                </IconButton>
              </Tooltip>
              <Tooltip title="Share activity">
                <IconButton
                  onClick={() => onShare(activity)}
                  color="primary"
                  size="small"
                  sx={{
                    transition: 'transform 0.2s',
                    '&:hover': {
                      transform: 'scale(1.1)',
                    },
                  }}
                >
                  <Share />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mb: 2,
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              lineHeight: 1.5,
            }}
          >
            {activity.description}
          </Typography>

          <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
            <motion.div variants={chipVariants}>
              <Chip
                icon={<Timer />}
                label={`${activity.duration} min`}
                size="small"
                color="primary"
                variant="outlined"
                sx={{ borderRadius: 1 }}
              />
            </motion.div>
            <motion.div variants={chipVariants}>
              <Chip
                icon={<TrendingUp />}
                label={activity.difficulty}
                size="small"
                sx={{
                  borderRadius: 1,
                  borderColor: getDifficultyColor(activity.difficulty),
                  color: getDifficultyColor(activity.difficulty),
                }}
                variant="outlined"
              />
            </motion.div>
            {activity.categories?.map((category) => (
              <motion.div key={category} variants={chipVariants}>
                <Chip
                  label={category}
                  size="small"
                  variant="outlined"
                  sx={{ borderRadius: 1 }}
                />
              </motion.div>
            ))}
          </Stack>

          {progress > 0 && (
            <Box sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Progress
                </Typography>
                <Typography variant="body2" color="primary" fontWeight="bold">
                  {Math.round(progress * 100)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={progress * 100}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: theme.palette.grey[200],
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 4,
                    background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
                  },
                }}
              />
            </Box>
          )}

          <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Rating
              value={4.5}
              precision={0.5}
              readOnly
              size="small"
              icon={<Star fontSize="inherit" />}
              emptyIcon={<StarBorder fontSize="inherit" />}
            />
            <Typography variant="body2" color="text.secondary">
              (4.5)
            </Typography>
          </Box>
        </CardContent>

        <CardActions sx={{ p: 2, pt: 0 }}>
          <Button
            variant="contained"
            fullWidth
            onClick={() => onStart(activity)}
            startIcon={<EmojiEmotions />}
            sx={{
              borderRadius: 2,
              textTransform: 'none',
              py: 1.5,
              background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.primary.light} 90%)`,
              boxShadow: `0 3px 5px 2px ${theme.palette.primary.light}40`,
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: `0 5px 8px 2px ${theme.palette.primary.light}60`,
              },
            }}
          >
            Start Activity
          </Button>
        </CardActions>
      </Card>
    </motion.div>
  );
};

export default ActivityCard; 