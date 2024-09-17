import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface PrivateRouteProps {
  children: React.ReactNode;
}

// Protect Routes so only logged in users can access this routes
const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const { isLoggedIn } = useAuth();

  if (!isLoggedIn()) {
    // If the user is not logged in, redirect to the login page
    return <Navigate to="/login" replace />;
  }

  // If the user is logged in, allow access to the route
  return <>{children}</>;
};

export default PrivateRoute;
