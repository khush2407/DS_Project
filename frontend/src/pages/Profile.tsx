import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Paper,
  Button,
  Avatar,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  useTheme,
} from '@mui/material';
import {
  Logout as LogoutIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  Favorite as FavoriteIcon,
  History as HistoryIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useApp } from '../context/AppContext';

const Profile: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { resetSession, isLoading } = useApp();
  
  const handleSignOut = async () => {
    try {
      // Clear tokens from localStorage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // Reset the session in the context
      await resetSession();
      
      // Redirect to login page
      navigate('/login', { replace: true });
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  const pageVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
  };

  if (isLoading) {
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
    <Container maxWidth="md" sx={{ py: 4 }}>
      <motion.div
        variants={pageVariants}
        initial="hidden"
        animate="visible"
      >
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Your Profile
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage your account and preferences
          </Typography>
        </Box>

        <Paper 
          elevation={0} 
          sx={{ 
            p: 4, 
            mb: 4, 
            borderRadius: 3,
            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)',
            background: 'linear-gradient(135deg, #FFFFFF 0%, #F8F8F8 100%)',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Avatar
              sx={{
                width: 80,
                height: 80,
                background: 'linear-gradient(135deg, #FF6B98 0%, #D84275 100%)',
                boxShadow: '0 4px 12px rgba(255, 107, 152, 0.3)',
                mr: 3,
              }}
            >
              <PersonIcon sx={{ fontSize: 40 }} />
            </Avatar>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                Sister
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Your Feminine Journey
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 3 }} />

          <List sx={{ py: 1 }}>
            <ListItem 
              button 
              sx={{ 
                borderRadius: 2, 
                mb: 1,
                '&:hover': {
                  backgroundColor: 'rgba(255, 107, 152, 0.08)',
                }
              }}
            >
              <ListItemIcon sx={{ color: theme.palette.primary.main }}>
                <FavoriteIcon />
              </ListItemIcon>
              <ListItemText 
                primary="Favorite Activities" 
                secondary="View and manage your favorite activities"
              />
            </ListItem>
            
            <ListItem 
              button 
              sx={{ 
                borderRadius: 2, 
                mb: 1,
                '&:hover': {
                  backgroundColor: 'rgba(255, 107, 152, 0.08)',
                }
              }}
            >
              <ListItemIcon sx={{ color: theme.palette.primary.main }}>
                <HistoryIcon />
              </ListItemIcon>
              <ListItemText 
                primary="Activity History" 
                secondary="Review your past activities and progress"
              />
            </ListItem>
            
            <ListItem 
              button 
              sx={{ 
                borderRadius: 2, 
                mb: 1,
                '&:hover': {
                  backgroundColor: 'rgba(255, 107, 152, 0.08)',
                }
              }}
            >
              <ListItemIcon sx={{ color: theme.palette.primary.main }}>
                <SettingsIcon />
              </ListItemIcon>
              <ListItemText 
                primary="Account Settings" 
                secondary="Update your profile and preferences"
              />
            </ListItem>
          </List>

          <Divider sx={{ my: 3 }} />

          <Button
            variant="outlined"
            color="error"
            startIcon={<LogoutIcon />}
            onClick={handleSignOut}
            sx={{
              borderRadius: 8,
              py: 1.5,
              px: 3,
              textTransform: 'none',
              fontWeight: 600,
              borderWidth: 2,
              '&:hover': {
                borderWidth: 2,
                backgroundColor: 'rgba(211, 47, 47, 0.04)',
              }
            }}
          >
            Sign Out
          </Button>
        </Paper>
      </motion.div>
    </Container>
  );
};

export default Profile;