import React from 'react';
import {
    AppBar,
    Box,
    CssBaseline,
    Drawer,
    IconButton,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Toolbar,
    Typography,
    useTheme,
    Avatar,
    Divider,
    Badge,
    Tooltip,
} from '@mui/material';
import {
    Menu as MenuIcon,
    Home as HomeIcon,
    Psychology as PsychologyIcon,
    Healing as HealingIcon,
    Timeline as TimelineIcon,
    Settings as SettingsIcon,
    Notifications as NotificationsIcon,
    AccountCircle as AccountIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const drawerWidth = 260;

interface LayoutProps {
    children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    const [mobileOpen, setMobileOpen] = React.useState(false);
    const theme = useTheme();
    const navigate = useNavigate();
    const location = useLocation();

    const menuItems = [
        { text: 'Home', icon: <HomeIcon />, path: '/' },
        { text: 'Emotional Wisdom', icon: <PsychologyIcon />, path: '/emotions' },
        { text: 'Mental Health Resources', icon: <HealingIcon />, path: '/resources' },
        { text: 'Wellness Journey', icon: <TimelineIcon />, path: '/trends' },
    ];

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    const drawer = (
        <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
        >
            <Box sx={{
                p: 3,
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                background: 'linear-gradient(135deg, #FFD0E0 0%, #FFE0EB 100%)',
                borderBottom: '1px solid rgba(0,0,0,0.06)'
            }}>
                <Avatar
                    sx={{
                        background: 'linear-gradient(135deg, #FF6B98 0%, #D84275 100%)',
                        width: 48,
                        height: 48,
                        boxShadow: '0 4px 12px rgba(255, 107, 152, 0.3)',
                    }}
                >
                    <AccountIcon />
                </Avatar>
                <Box>
                    <Typography
                        variant="subtitle1"
                        sx={{
                            fontWeight: 'bold',
                            color: '#2A2A2A',
                            fontFamily: '"Montserrat", sans-serif',
                        }}
                    >
                        Welcome, Sister
                    </Typography>
                    <Typography
                        variant="body2"
                        sx={{
                            color: '#6E6E6E',
                            fontWeight: 500
                        }}
                    >
                        Your Feminine Journey
                    </Typography>
                </Box>
            </Box>
            <List sx={{ px: 2, py: 3, backgroundColor: '#FFFFFF' }}>
                {menuItems.map((item) => (
                    <ListItem
                        button
                        key={item.text}
                        onClick={() => {
                            navigate(item.path);
                            setMobileOpen(false);
                        }}
                        selected={location.pathname === item.path}
                        sx={{
                            borderRadius: 8,
                            mb: 1.5,
                            py: 1.2,
                            transition: 'all 0.2s ease',
                            '&.Mui-selected': {
                                backgroundColor: '#FFE0EB',
                                '&:hover': {
                                    backgroundColor: '#FFD0E0',
                                },
                            },
                            '&:hover': {
                                backgroundColor: '#F5F5F5',
                                transform: 'translateX(4px)',
                            },
                        }}
                    >
                        <ListItemIcon
                            sx={{
                                color: location.pathname === item.path
                                    ? '#FF6B98'
                                    : '#6E6E6E',
                                minWidth: 40,
                            }}
                        >
                            {item.icon}
                        </ListItemIcon>
                        <ListItemText
                            primary={item.text}
                            primaryTypographyProps={{
                                fontWeight: location.pathname === item.path ? 700 : 500,
                                fontFamily: '"Montserrat", sans-serif',
                                fontSize: '0.95rem',
                            }}
                            sx={{
                                color: location.pathname === item.path
                                    ? '#2A2A2A'
                                    : '#6E6E6E',
                            }}
                        />
                    </ListItem>
                ))}
            </List>
        </motion.div>
    );

    return (
        <Box sx={{ display: 'flex' }}>
            <CssBaseline />
            <AppBar
                position="fixed"
                elevation={0}
                sx={{
                    width: { sm: `calc(100% - ${drawerWidth}px)` },
                    ml: { sm: `${drawerWidth}px` },
                    backgroundColor: '#FFFFFF',
                    borderBottom: '1px solid rgba(0,0,0,0.06)',
                }}
            >
                <Toolbar sx={{ height: 70 }}>
                    <IconButton
                        color="inherit"
                        aria-label="open drawer"
                        edge="start"
                        onClick={handleDrawerToggle}
                        sx={{
                            mr: 2,
                            display: { sm: 'none' },
                            color: '#FF6B98',
                            '&:hover': {
                                backgroundColor: 'rgba(255, 107, 152, 0.08)'
                            }
                        }}
                    >
                        <MenuIcon />
                    </IconButton>
                    <Typography
                        variant="h6"
                        noWrap
                        component="div"
                        sx={{
                            flexGrow: 1,
                            color: '#2A2A2A',
                            fontFamily: '"Montserrat", sans-serif',
                            fontWeight: 'bold',
                            letterSpacing: '-0.01em'
                        }}
                    >
                        Women's Emotional Wellness Sanctuary
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Profile">
                            <IconButton
                                component={Link}
                                to="/profile"
                                sx={{
                                    color: '#FF6B98',
                                    backgroundColor: 'rgba(255, 107, 152, 0.08)',
                                    '&:hover': {
                                        backgroundColor: 'rgba(255, 107, 152, 0.15)'
                                    }
                                }}
                            >
                                <AccountIcon />
                            </IconButton>
                        </Tooltip>
                    </Box>
                </Toolbar>
            </AppBar>
            <Box
                component="nav"
                sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
            >
                <Drawer
                    variant="temporary"
                    open={mobileOpen}
                    onClose={handleDrawerToggle}
                    ModalProps={{
                        keepMounted: true,
                    }}
                    sx={{
                        display: { xs: 'block', sm: 'none' },
                        '& .MuiDrawer-paper': {
                            boxSizing: 'border-box',
                            width: drawerWidth,
                            borderRight: '1px solid rgba(0,0,0,0.06)',
                            backgroundColor: '#FFFFFF',
                        },
                    }}
                >
                    {drawer}
                </Drawer>
                <Drawer
                    variant="permanent"
                    sx={{
                        display: { xs: 'none', sm: 'block' },
                        '& .MuiDrawer-paper': {
                            boxSizing: 'border-box',
                            width: drawerWidth,
                            borderRight: '1px solid rgba(0,0,0,0.06)',
                            backgroundColor: '#FFFFFF',
                        },
                    }}
                    open
                >
                    {drawer}
                </Drawer>
            </Box>
            <Box
                component="main"
                sx={{
                    flexGrow: 1,
                    p: 4,
                    width: { sm: `calc(100% - ${drawerWidth}px)` },
                    minHeight: '100vh',
                    backgroundColor: '#FAFAFA',
                }}
            >
                <Toolbar />
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                >
                    {children}
                </motion.div>
            </Box>
        </Box>
    );
};

export default Layout; 