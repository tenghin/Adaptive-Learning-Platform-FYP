import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { authService } from '../services/authService';
import {
  clearStoredToken,
  getStoredToken,
  removeStoredToken,
  setStoredToken,
} from '../utils/storage';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(getStoredToken());
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const syncProfile = useCallback(async () => {
    const storedToken = getStoredToken();
    setToken(storedToken);

    if (!storedToken) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const profileData = await authService.getProfile();
      setUser(profileData.user);
    } catch {
      removeStoredToken();
      setToken('');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    syncProfile();

    const handleAuthChange = () => {
      syncProfile();
    };

    window.addEventListener('adaptive-auth-changed', handleAuthChange);

    return () => {
      window.removeEventListener('adaptive-auth-changed', handleAuthChange);
    };
  }, [syncProfile]);

  const login = useCallback(async (credentials) => {
    const responseData = await authService.login(credentials);
    setStoredToken(responseData.access_token);
    setToken(responseData.access_token);
    setUser(responseData.user);
    return responseData.user;
  }, []);

  const register = useCallback(async (payload) => {
    const responseData = await authService.register(payload);
    return responseData.user;
  }, []);

  const logout = useCallback(() => {
    clearStoredToken();
    setToken('');
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      isAuthenticated: Boolean(token),
      login,
      register,
      logout,
      refreshProfile: syncProfile,
    }),
    [login, loading, logout, syncProfile, token, user, register]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }

  return context;
}
