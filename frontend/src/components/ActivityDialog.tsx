import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  LinearProgress,
  IconButton,
  useTheme,
  Chip,
} from '@mui/material';
import {
  Close,
  Timer,
  TrendingUp,
  EmojiEmotions,
  CheckCircle,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity } from '../types';

interface ActivityDialogProps {
  activity: Activity | null;
  open: boolean;
  onClose: () => void;
  onStart: () => void;
  progress?: number;
}

const ActivityDialog: React.FC<ActivityDialogProps> = ({
  activity,
  open,
  onClose,
  onStart,
  progress = 0,
}) => {
  const theme = useTheme();

  if (!activity) return null;

  const dialogVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          overflow: 'hidden',
        },
      }}
    >
      <motion.div
        variants={dialogVariants}
        initial="hidden"
        animate="visible"
        exit="exit"
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h5" component="div">
              {activity.title}
            </Typography>
            <IconButton onClick={onClose} size="small">
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent>
          <Box sx={{ mb: 3 }}>
            <Typography variant="body1" color="text.secondary" paragraph>
              {activity.description}
            </Typography>

            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
              <Chip
                icon={<Timer />}
                label={`${activity.duration} min`}
                color="primary"
                variant="outlined"
              />
              <Chip
                icon={<TrendingUp />}
                label={activity.difficulty}
                color="secondary"
                variant="outlined"
              />
              {activity.categories?.map((category) => (
                <Chip
                  key={category}
                  label={category}
                  variant="outlined"
                />
              ))}
            </Box>

            {progress > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Progress: {Math.round(progress * 100)}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={progress * 100}
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

            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Steps:
              </Typography>
              {activity.steps?.map((step, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      mb: 1,
                      p: 1,
                      borderRadius: 1,
                      backgroundColor: theme.palette.background.default,
                    }}
                  >
                    <Box
                      sx={{
                        width: 24,
                        height: 24,
                        borderRadius: '50%',
                        backgroundColor: theme.palette.primary.main,
                        color: theme.palette.primary.contrastText,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mr: 2,
                      }}
                    >
                      {index + 1}
                    </Box>
                    <Typography variant="body2">{step}</Typography>
                  </Box>
                </motion.div>
              ))}
            </Box>
          </Box>
        </DialogContent>

        <DialogActions sx={{ p: 2, pt: 0 }}>
          <Button
            variant="outlined"
            onClick={onClose}
            sx={{ mr: 1 }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={onStart}
            startIcon={progress > 0 ? <CheckCircle /> : <EmojiEmotions />}
            sx={{
              borderRadius: 2,
              textTransform: 'none',
              px: 3,
            }}
          >
            {progress > 0 ? 'Continue Activity' : 'Start Activity'}
          </Button>
        </DialogActions>
      </motion.div>
    </Dialog>
  );
};

export default ActivityDialog; 