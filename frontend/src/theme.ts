import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    palette: {
        primary: {
            main: '#FF6B98', // Modern pink
            light: '#FFD0E0',
            dark: '#D84275',
            contrastText: '#FFFFFF',
        },
        secondary: {
            main: '#7E57C2', // Modern purple
            light: '#B085F5',
            dark: '#4D2C91',
            contrastText: '#FFFFFF',
        },
        background: {
            default: '#FAFAFA', // Lighter, more modern background
            paper: '#FFFFFF',   // Clean white for cards
        },
        text: {
            primary: '#2A2A2A', // Near-black for better readability
            secondary: '#6E6E6E', // Modern gray
        },
        success: {
            main: '#4CAF50',
            light: '#A5D6A7',
            dark: '#2E7D32',
        },
        warning: {
            main: '#FFC107',
            light: '#FFE082',
            dark: '#FFA000',
        },
        error: {
            main: '#F44336',
            light: '#E57373',
            dark: '#C62828',
        },
    },
    typography: {
        fontFamily: '"Montserrat", "Inter", "Roboto", "Helvetica", "Arial", sans-serif',
        h1: {
            fontWeight: 700,
            fontSize: '2.5rem',
            letterSpacing: '-0.01562em',
        },
        h2: {
            fontWeight: 700,
            fontSize: '2rem',
            letterSpacing: '-0.00833em',
        },
        h3: {
            fontWeight: 600,
            fontSize: '1.75rem',
            letterSpacing: '0em',
        },
        h4: {
            fontWeight: 600,
            fontSize: '1.5rem',
            letterSpacing: '0.00735em',
        },
        h5: {
            fontWeight: 600,
            fontSize: '1.25rem',
            letterSpacing: '0em',
        },
        h6: {
            fontWeight: 600,
            fontSize: '1rem',
            letterSpacing: '0.0075em',
        },
        body1: {
            fontSize: '1rem',
            lineHeight: 1.6,
            letterSpacing: '0.00938em',
        },
        body2: {
            fontSize: '0.875rem',
            lineHeight: 1.6,
            letterSpacing: '0.01071em',
        },
        button: {
            textTransform: 'none',
            fontWeight: 600,
            letterSpacing: '0.02857em',
        },
    },
    shape: {
        borderRadius: 12,
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    borderRadius: 8,
                    padding: '10px 24px',
                    fontWeight: 600,
                    textTransform: 'none',
                    fontFamily: '"Montserrat", sans-serif',
                    transition: 'all 0.2s ease-in-out',
                },
                contained: {
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
                    '&:hover': {
                        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.12)',
                        transform: 'translateY(-2px)',
                    },
                },
                outlined: {
                    borderWidth: '1.5px',
                    '&:hover': {
                        borderWidth: '1.5px',
                    },
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    borderRadius: 12,
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)',
                    border: 'none',
                    overflow: 'hidden',
                    transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                    '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 8px 30px rgba(0, 0, 0, 0.08)',
                    },
                },
            },
        },
        MuiPaper: {
            styleOverrides: {
                root: {
                    borderRadius: 12,
                    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.05)',
                },
                elevation1: {
                    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.05)',
                },
                elevation2: {
                    boxShadow: '0 4px 16px rgba(0, 0, 0, 0.08)',
                },
                elevation3: {
                    boxShadow: '0 6px 20px rgba(0, 0, 0, 0.1)',
                },
            },
        },
        MuiTextField: {
            styleOverrides: {
                root: {
                    '& .MuiOutlinedInput-root': {
                        borderRadius: 8,
                        transition: 'box-shadow 0.2s ease',
                        '&:hover': {
                            boxShadow: '0 0 0 1px rgba(255, 107, 152, 0.2)',
                        },
                        '&.Mui-focused': {
                            boxShadow: '0 0 0 2px rgba(255, 107, 152, 0.2)',
                            '& fieldset': {
                                borderColor: '#FF6B98',
                                borderWidth: 2,
                            },
                        },
                    },
                    '& .MuiInputLabel-root.Mui-focused': {
                        color: '#D84275',
                    },
                },
            },
        },
        MuiListItem: {
            styleOverrides: {
                root: {
                    borderRadius: 8,
                    transition: 'background-color 0.2s ease',
                },
            },
        },
        MuiChip: {
            styleOverrides: {
                root: {
                    borderRadius: 8,
                    backgroundColor: '#FFE0EB',
                    color: '#D84275',
                    fontWeight: 500,
                    transition: 'all 0.2s ease',
                    '&:hover': {
                        backgroundColor: '#FFD0E0',
                        transform: 'translateY(-1px)',
                    },
                },
                outlined: {
                    borderWidth: '1.5px',
                    '&:hover': {
                        borderWidth: '1.5px',
                    },
                },
            },
        },
        MuiAppBar: {
            styleOverrides: {
                root: {
                    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
                },
            },
        },
        MuiDrawer: {
            styleOverrides: {
                paper: {
                    boxShadow: '2px 0 10px rgba(0, 0, 0, 0.05)',
                },
            },
        },
        MuiLinearProgress: {
            styleOverrides: {
                root: {
                    borderRadius: 4,
                    height: 8,
                },
            },
        },
        MuiDivider: {
            styleOverrides: {
                root: {
                    borderColor: 'rgba(0, 0, 0, 0.06)',
                },
            },
        },
    },
});

export default theme; 