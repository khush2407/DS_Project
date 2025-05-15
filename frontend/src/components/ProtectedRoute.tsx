import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

interface ProtectedRouteProps {
    children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    // Bypass authentication check - allow direct access to all routes
    return <>{children}</>;
    
    /* Original authentication logic (commented out)
    const location = useLocation();
    const isAuthenticated = !!localStorage.getItem('access_token');

    if (!isAuthenticated) {
        // Redirect to login page but save the attempted url
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return <>{children}</>;
    */
};

export default ProtectedRoute; 