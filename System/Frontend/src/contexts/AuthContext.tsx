import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { saveAuthData, getAuthData, clearAuthData } from '../services/authentication/authService';
import { jwtDecode } from 'jwt-decode';
import { useNavigate } from 'react-router-dom';

interface AuthContextType {
  token: string;
  role: string;
  userID: string;
  setAuthData: (token: string, role: string, userID: string) => void;
  clearAuth: () => void;
  isLoggedIn: () => boolean;
  getAndCheckToken: () => string;
}

// Store Auth Data and make it accessable for the whole frontend
const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const [auth, setAuth] = useState(getAuthData());

  useEffect(() => {
    // Update auth state when the token is retrieved from localStorage
    setAuth(getAuthData());
  }, []);

  
  // Save JWT, role and userID to localStorage
  const setAuthData = (token: string, role: string, userID: string ) => {
    setAuth({ token, role, userID });
    saveAuthData(token, role, userID); // Save to localStorage
  };

   // Clear data from localStorage
  const clearAuth = () => {
    setAuth({ token: '', role: '', userID: '' });
    clearAuthData();
  };

  // Check if User is logged in
  const isLoggedIn = () => {
    checkToken() 
    return Boolean(auth.token);
  };

  // Check JWT token and return it
  const getAndCheckToken = () => {
    checkToken();
     return auth.token;
   }

  // Check if JWT token is valid an not expired. If expired logout the user
  const checkToken = () => {
    if (auth.token) {
      try {
        const decoded = jwtDecode<{ exp: number }>(auth.token); 
        const currentTime = Date.now() / 1000; 
        if (decoded.exp < currentTime) {
          clearAuth();
          navigate('/login', { state: { message: 'Your session has expired. Please log in again.' } });
        }
      } catch (error) {
        console.error('Invalid token:', error);
        clearAuth();
        navigate('/login', { state: { message: 'Your session has expired. Please log in again.' } });
      }
    }
  };

  return (
    <AuthContext.Provider value={{ ...auth, setAuthData, clearAuth, isLoggedIn, getAndCheckToken }}>
      {children}
    </AuthContext.Provider>
  );
};



export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};