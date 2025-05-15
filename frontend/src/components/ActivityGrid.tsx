import React, { useState, useMemo } from 'react';
import {
  Grid,
  Container,
  Typography,
  Box,
  TextField,
  InputAdornment,
  Chip,
  Stack,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Sort as SortIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import ActivityCard from './ActivityCard';
import { Activity } from '../types';

interface ActivityGridProps {
  activities: Activity[];
  onStartActivity: (activity: Activity) => void;
  onFavoriteActivity: (activityId: string) => void;
  onShareActivity: (activity: Activity) => void;
  favoriteActivities: string[];
  activityProgress: Record<string, number>;
}

const ActivityGrid: React.FC<ActivityGridProps> = ({
  activities,
  onStartActivity,
  onFavoriteActivity,
  onShareActivity,
  favoriteActivities,
  activityProgress,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedDifficulty, setSelectedDifficulty] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'popular' | 'newest' | 'duration'>('popular');

  const categories = useMemo(() => {
    const uniqueCategories = new Set<string>();
    activities.forEach(activity => {
      activity.categories.forEach(category => uniqueCategories.add(category));
    });
    return Array.from(uniqueCategories);
  }, [activities]);

  const difficulties = ['beginner', 'intermediate', 'advanced'];

  const filteredActivities = useMemo(() => {
    return activities.filter(activity => {
      const matchesSearch = activity.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          activity.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategories = selectedCategories.length === 0 ||
                              activity.categories.some(cat => selectedCategories.includes(cat));
      const matchesDifficulty = !selectedDifficulty ||
                              activity.difficulty.toLowerCase() === selectedDifficulty.toLowerCase();
      return matchesSearch && matchesCategories && matchesDifficulty;
    }).sort((a, b) => {
      switch (sortBy) {
        case 'popular':
          return (b.rating || 0) - (a.rating || 0);
        case 'newest':
          return new Date(b.created_at || '').getTime() - new Date(a.created_at || '').getTime();
        case 'duration':
          return a.duration - b.duration;
        default:
          return 0;
      }
    });
  }, [activities, searchQuery, selectedCategories, selectedDifficulty, sortBy]);

  const handleCategoryToggle = (category: string) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const handleDifficultyToggle = (difficulty: string) => {
    setSelectedDifficulty(prev => prev === difficulty ? null : difficulty);
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

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Activities
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Discover and engage with activities designed to improve your mental wellness
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search activities..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            sx={{ maxWidth: 400 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Filter">
              <IconButton color="primary">
                <FilterIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Sort">
              <IconButton color="primary">
                <SortIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <Stack direction="row" spacing={1} sx={{ mb: 3, flexWrap: 'wrap', gap: 1 }}>
          {categories.map(category => (
            <Chip
              key={category}
              label={category}
              onClick={() => handleCategoryToggle(category)}
              color={selectedCategories.includes(category) ? 'primary' : 'default'}
              variant={selectedCategories.includes(category) ? 'filled' : 'outlined'}
              sx={{ borderRadius: 1 }}
            />
          ))}
        </Stack>

        <Stack direction="row" spacing={1} sx={{ mb: 3 }}>
          {difficulties.map(difficulty => (
            <Chip
              key={difficulty}
              label={difficulty}
              onClick={() => handleDifficultyToggle(difficulty)}
              color={selectedDifficulty === difficulty ? 'primary' : 'default'}
              variant={selectedDifficulty === difficulty ? 'filled' : 'outlined'}
              sx={{
                borderRadius: 1,
                borderColor: theme.palette[difficulty === 'beginner' ? 'success' : 
                                         difficulty === 'intermediate' ? 'warning' : 'error'].main,
                color: selectedDifficulty === difficulty ? 'white' : 
                       theme.palette[difficulty === 'beginner' ? 'success' : 
                                   difficulty === 'intermediate' ? 'warning' : 'error'].main,
              }}
            />
          ))}
        </Stack>
      </Box>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <Grid container spacing={3}>
          {filteredActivities.map(activity => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={activity.id}>
              <ActivityCard
                activity={activity}
                onStart={() => onStartActivity(activity)}
                onFavorite={() => onFavoriteActivity(activity.id)}
                onShare={() => onShareActivity(activity)}
                isFavorite={favoriteActivities.includes(activity.id)}
                progress={activityProgress[activity.id]}
              />
            </Grid>
          ))}
        </Grid>
      </motion.div>

      {filteredActivities.length === 0 && (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            py: 8,
            textAlign: 'center',
          }}
        >
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No activities found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your search or filters
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default ActivityGrid; 