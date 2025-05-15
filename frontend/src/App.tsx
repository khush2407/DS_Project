import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { AppProvider } from './context/AppContext';
import theme from './theme';
import Home from './pages/Home';
import Layout from './components/Layout';
import EmotionAnalysis from './pages/EmotionAnalysis';
import MentalHealthResources from './pages/MentalHealthResources';
import EmotionTrends from './pages/EmotionTrends';
import Settings from './pages/Settings';
import Profile from './pages/Profile';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ProtectedRoute from './components/ProtectedRoute';

const App: React.FC = () => {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <AppProvider>
                <Router>
                    <Routes>
                        {/* Public routes */}
                        <Route path="/login" element={<Login />} />
                        <Route path="/signup" element={<Signup />} />
                        
                        {/* Protected routes */}
                        <Route path="/" element={
                            <ProtectedRoute>
                                <Layout>
                                    <Home />
                                </Layout>
                            </ProtectedRoute>
                        } />
                        <Route path="/emotions" element={
                            <ProtectedRoute>
                                <Layout>
                                    <EmotionAnalysis />
                                </Layout>
                            </ProtectedRoute>
                        } />
                        <Route path="/resources" element={
                            <ProtectedRoute>
                                <Layout>
                                    <MentalHealthResources />
                                </Layout>
                            </ProtectedRoute>
                        } />
                        <Route path="/trends" element={
                            <ProtectedRoute>
                                <Layout>
                                    <EmotionTrends />
                                </Layout>
                            </ProtectedRoute>
                        } />
                        <Route path="/settings" element={
                            <ProtectedRoute>
                                <Layout>
                                    <Settings />
                                </Layout>
                            </ProtectedRoute>
                            } />
                            <Route path="/profile" element={
                                <ProtectedRoute>
                                    <Layout>
                                        <Profile />
                                    </Layout>
                                </ProtectedRoute>
                            } />
                            
                            {/* Catch all route - redirect to home */}
                            <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </Router>
            </AppProvider>
        </ThemeProvider>
    );
};

export default App;
