import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { saveAuthData, getAuthData, clearAuthData } from '../services/authentication/authService';

interface AuthContextType {
  token: string;
  role: string;
  userID: string;
  setAuthData: (token: string, role: string, userID: string) => void;
  clearAuth: () => void;
  isLoggedIn: () => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [auth, setAuth] = useState(getAuthData());

  useEffect(() => {
    // Update auth state when the token is retrieved from localStorage
    setAuth(getAuthData());
  }, []);

  const setAuthData = (token: string, role: string, userID: string ) => {
    setAuth({ token, role, userID });
    saveAuthData(token, role, userID); // Save to localStorage
  };

  const clearAuth = () => {
    setAuth({ token: '', role: '', userID: '' });
    clearAuthData(); // Clear from localStorage
  };

  const isLoggedIn = () => {
    return Boolean(auth.token);
  };

  return (
    <AuthContext.Provider value={{ ...auth, setAuthData, clearAuth, isLoggedIn }}>
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