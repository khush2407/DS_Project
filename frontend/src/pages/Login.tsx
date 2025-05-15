import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
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
import { login } from '../services/api';
import { LoginData, Token } from '../types';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [formData, setFormData] = useState<LoginData>({
    username: '',
    password: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    // Check for success message from navigation state
    const message = location.state?.message;
    if (message) {
      setSuccess(message);
    }
  }, [location]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!formData.username || !formData.password) {
      setError('All fields are required');
      return;
    }

    try {
      setLoading(true);
      const response = await login(formData);
      
      // Store tokens in localStorage
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      
      // Redirect to the page they tried to access, or dashboard
      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
    } catch (err: any) {
      console.error('Login error:', err);
      
      // Provide more specific error messages based on the error
      if (!err.response) {
        setError('Network error. Please check your internet connection.');
      } else if (err.response.status === 401) {
        setError('Invalid email or password. Please try again.');
      } else if (err.response.status === 500) {
        setError('Server error. Please try again later.');
      } else {
        setError(err.response?.data?.detail || 'An error occurred during login. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, mb: 4 }}>
        <Paper
          elevation={2}
          sx={{
            p: 5,
            borderRadius: 3,
            backgroundColor: '#FFFFFF',
            border: 'none',
            boxShadow: '0 10px 30px rgba(0, 0, 0, 0.08)',
          }}
        >
          <Typography
            variant="h4"
            component="h1"
            gutterBottom
            align="center"
            sx={{
              color: '#2A2A2A',
              fontFamily: '"Montserrat", sans-serif',
              fontWeight: 700,
              mb: 2,
              letterSpacing: '-0.01em'
            }}
          >
            Welcome Back
          </Typography>
          
          <Typography
            variant="body1"
            align="center"
            sx={{
              mb: 4,
              color: '#6E6E6E',
              fontSize: '1.05rem'
            }}
          >
            Your women's wellness journey continues here
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {success}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              name="username"
              type="email"
              value={formData.username}
              onChange={handleChange}
              margin="normal"
              required
              sx={{
                mb: 3,
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
                '& .MuiInputLabel-root.Mui-focused': {
                  color: '#D84275',
                },
                '& .MuiInputBase-input': {
                  padding: '16px 14px',
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
                '& .MuiInputLabel-root.Mui-focused': {
                  color: '#D84275',
                },
                '& .MuiInputBase-input': {
                  padding: '16px 14px',
                },
              }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                      sx={{
                        color: '#6E6E6E',
                        '&:hover': {
                          backgroundColor: 'rgba(255, 107, 152, 0.08)',
                          color: '#FF6B98'
                        }
                      }}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
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
                background: 'linear-gradient(90deg, #FF6B98 0%, #D84275 100%)',
                borderRadius: 8,
                padding: '14px 24px',
                textTransform: 'none',
                fontSize: '1.1rem',
                fontWeight: 600,
                boxShadow: '0 4px 12px rgba(255, 107, 152, 0.25)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  boxShadow: '0 6px 16px rgba(255, 107, 152, 0.35)',
                  transform: 'translateY(-2px)',
                },
                '&.Mui-disabled': {
                  background: 'linear-gradient(90deg, #E0E0E0 0%, #BDBDBD 100%)',
                  color: '#757575',
                  boxShadow: 'none',
                }
              }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Continue Your Journey'}
            </Button>
          </form>

          <Box sx={{ mt: 4, textAlign: 'center', p: 2, borderTop: '1px solid rgba(0, 0, 0, 0.06)' }}>
            <Typography
              variant="body1"
              sx={{
                color: '#6E6E6E',
                fontSize: '1rem'
              }}
            >
              New to our women's wellness community?
            </Typography>
            <Button
              onClick={() => navigate('/signup')}
              variant="outlined"
              sx={{
                textTransform: 'none',
                color: '#7E57C2',
                fontWeight: 600,
                fontSize: '1rem',
                mt: 2,
                borderColor: '#7E57C2',
                borderRadius: 8,
                padding: '8px 24px',
                borderWidth: '1.5px',
                transition: 'all 0.2s ease',
                '&:hover': {
                  backgroundColor: 'rgba(126, 87, 194, 0.08)',
                  borderWidth: '1.5px',
                  borderColor: '#4D2C91',
                  transform: 'translateY(-2px)',
                }
              }}
            >
              Join Our Sisterhood
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;
