import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { signup } from '../services/api';
import { SignupData, User } from '../types';

const Signup: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<SignupData>({
    email: '',
    username: '',
    full_name: '',
    password: '',
    confirm_password: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = () => {
    if (!formData.email || !formData.username || !formData.password || !formData.confirm_password) {
      setError('All fields are required');
      return false;
    }
    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match');
      return false;
    }
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      await signup(formData);
      navigate('/login', { state: { message: 'Registration successful! Please login.' } });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred during signup');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, mb: 4 }}>
        <Paper
          elevation={3}
          sx={{
            p: 5,
            borderRadius: 4,
            backgroundColor: '#fff0f5',
            border: '1px solid #f8bbd0',
            boxShadow: '0 8px 20px rgba(216, 79, 139, 0.15)',
          }}
        >
          <Typography
            variant="h4"
            component="h1"
            gutterBottom
            align="center"
            sx={{
              color: '#ad1457',
              fontFamily: '"Playfair Display", serif',
              fontWeight: 'bold',
              mb: 3
            }}
          >
            Join Our Women's Community
          </Typography>
          
          <Typography
            variant="body1"
            align="center"
            sx={{
              mb: 4,
              color: '#6a1b9a',
              fontStyle: 'italic'
            }}
          >
            Begin your journey to emotional wellness and self-discovery
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              margin="normal"
              required
              sx={{
                mb: 3,
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  backgroundColor: '#fef6f9',
                  '&.Mui-focused fieldset': {
                    borderColor: '#d84f8b',
                    borderWidth: 2,
                  },
                },
                '& .MuiInputLabel-root.Mui-focused': {
                  color: '#ad1457',
                },
              }}
            />
            <TextField
              fullWidth
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              margin="normal"
              required
              sx={{
                mb: 3,
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  backgroundColor: '#fef6f9',
                  '&.Mui-focused fieldset': {
                    borderColor: '#d84f8b',
                    borderWidth: 2,
                  },
                },
                '& .MuiInputLabel-root.Mui-focused': {
                  color: '#ad1457',
                },
              }}
            />
            <TextField
              fullWidth
              label="Full Name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              margin="normal"
              sx={{
                mb: 3,
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  backgroundColor: '#fef6f9',
                  '&.Mui-focused fieldset': {
                    borderColor: '#d84f8b',
                    borderWidth: 2,
                  },
                },
                '& .MuiInputLabel-root.Mui-focused': {
                  color: '#ad1457',
                },
              }}
            />
            <TextField
              fullWidth
              label="Password"
              name="password"
              type={showPassword ? "text" : "password"}
              value={formData.password}
              onChange={handleChange}
              margin="normal"
              required
              sx={{
                mb: 3,
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  backgroundColor: '#fef6f9',
                  '&.Mui-focused fieldset': {
                    borderColor: '#d84f8b',
                    borderWidth: 2,
                  },
                },
                '& .MuiInputLabel-root.Mui-focused': {
                  color: '#ad1457',
                },
              }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                      sx={{ color: '#ad1457' }}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <TextField
              fullWidth
              label="Confirm Password"
              name="confirm_password"
              type={showConfirmPassword ? "text" : "password"}
              value={formData.confirm_password}
              onChange={handleChange}
              margin="normal"
              required
              sx={{
                mb: 3,
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  backgroundColor: '#fef6f9',
                  '&.Mui-focused fieldset': {
                    borderColor: '#d84f8b',
                    borderWidth: 2,
                  },
                },
                '& .MuiInputLabel-root.Mui-focused': {
                  color: '#ad1457',
                },
              }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle confirm password visibility"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      edge="end"
                      sx={{ color: '#ad1457' }}
                    >
                      {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{
                mt: 4,
                mb: 2,
                backgroundColor: '#d84f8b',
                borderRadius: 28,
                padding: '12px 24px',
                textTransform: 'none',
                fontSize: '1.1rem',
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
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Begin Your Wellness Journey'}
            </Button>
          </form>

          <Box sx={{ mt: 4, textAlign: 'center', p: 2, borderTop: '1px solid #f8bbd0' }}>
            <Typography
              variant="body1"
              sx={{
                color: '#6a1b9a',
                fontStyle: 'italic'
              }}
            >
              Already part of our women's wellness community?
            </Typography>
            <Button
              onClick={() => navigate('/login')}
              sx={{
                textTransform: 'none',
                color: '#ad1457',
                fontWeight: 'bold',
                fontSize: '1rem',
                mt: 1,
                '&:hover': {
                  backgroundColor: '#fce4ec',
                }
              }}
            >
              Return to Your Journey
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Signup; 