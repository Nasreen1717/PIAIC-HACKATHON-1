/**
 * Authentication context for global auth state management.
 * Provides user info, JWT token, and auth methods to the entire app.
 */
import React, { createContext, useState, useCallback, useEffect } from 'react';

// Get API base URL from environment or default to localhost
const API_BASE_URL = typeof process !== 'undefined' && process.env?.REACT_APP_API_URL
  ? process.env.REACT_APP_API_URL
  : 'http://localhost:8000';

interface UserBackground {
  id?: number;
  user_id?: number;
  software_background?: string;
  hardware_background?: string;
  ros_experience?: string;
  python_level?: string;
  learning_goal?: string;
  available_hardware?: string;
}

interface User {
  id: number;
  email: string;
  full_name?: string;
  created_at: string;
  is_active: boolean;
  background?: UserBackground;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  signin: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  signup: (email: string, password: string, fullName: string, background?: Partial<UserBackground>) => Promise<void>;
  signout: () => Promise<void>;
  updateProfile: (updates: Partial<User>) => Promise<void>;
  clearError: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize from localStorage on mount and listen for changes
  useEffect(() => {
    const loadAuthState = () => {
      const storedToken = localStorage.getItem('auth_token');
      const storedUser = localStorage.getItem('auth_user');

      if (storedToken && storedUser) {
        try {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
        } catch (e) {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
        }
      }
    };

    // Load initial state
    loadAuthState();

    // Listen for storage changes (e.g., from other tabs or our own signin/signup)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'auth_token' || e.key === 'auth_user') {
        console.log('AuthContext: Storage changed, reloading auth state');
        loadAuthState();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const signin = useCallback(async (email: string, password: string, rememberMe = false) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/signin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          remember_me: rememberMe,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to sign in');
      }

      const { access_token } = await response.json();
      console.log('AuthContext: Sign in successful, storing token');
      setToken(access_token);
      localStorage.setItem('auth_token', access_token);

      // Fetch user profile
      const profileResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${access_token}`,
        },
      });

      if (profileResponse.ok) {
        const userProfile = await profileResponse.json();
        console.log('AuthContext: User profile loaded:', userProfile.email);
        setUser(userProfile);
        localStorage.setItem('auth_user', JSON.stringify(userProfile));
        // Dispatch custom event so other components know auth changed
        window.dispatchEvent(new CustomEvent('auth-changed', { detail: { user: userProfile, token: access_token } }));
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const signup = useCallback(async (
    email: string,
    password: string,
    fullName: string,
    background?: Partial<UserBackground>
  ) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
          ...background,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to sign up');
      }

      const { access_token } = await response.json();
      console.log('AuthContext: Sign up successful, storing token');
      setToken(access_token);
      localStorage.setItem('auth_token', access_token);

      // Fetch user profile
      const profileResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${access_token}`,
        },
      });

      if (profileResponse.ok) {
        const userProfile = await profileResponse.json();
        console.log('AuthContext: User profile loaded:', userProfile.email);
        setUser(userProfile);
        localStorage.setItem('auth_user', JSON.stringify(userProfile));
        // Dispatch custom event so other components know auth changed
        window.dispatchEvent(new CustomEvent('auth-changed', { detail: { user: userProfile, token: access_token } }));
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const signout = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      if (token) {
        await fetch(`${API_BASE_URL}/api/auth/signout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      }
    } catch (err) {
      console.error('Error during signout:', err);
    } finally {
      setToken(null);
      setUser(null);
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      setIsLoading(false);
    }
  }, [token]);

  const updateProfile = useCallback(async (updates: Partial<User>) => {
    if (!token || !user) {
      throw new Error('Not authenticated');
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/users/${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to update profile');
      }

      const updatedUser = await response.json();
      setUser(updatedUser);
      localStorage.setItem('auth_user', JSON.stringify(updatedUser));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [token, user]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        error,
        signin,
        signup,
        signout,
        updateProfile,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
