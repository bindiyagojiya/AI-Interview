import React, { createContext, useContext, useState, useEffect } from "react";
import { User, AuthResponse } from "../types";
import { apiClient } from "../services/api";
import { StorageService } from "../services/storage";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchCurrentUser = async () => {
    try {
      const response = await apiClient.get<User>("/auth/me");
      setUser(response.data);
      await StorageService.saveUserData(response.data);
    } catch {
      setUser(null);
      await StorageService.removeToken();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const initializeAuth = async () => {
      const token = await StorageService.getToken();
      if (token) {
        await fetchCurrentUser();
      } else {
        setIsLoading(false);
      }
    };
    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await apiClient.post<AuthResponse>("/auth/login", { email, password });
    await StorageService.saveToken(response.data.access_token);
    await fetchCurrentUser();
  };

  const register = async (email: string, password: string, fullName: string) => {
    await apiClient.post("/auth/register", {
      email,
      password,
      full_name: fullName,
    });
    // Auto-login after registration
    await login(email, password);
  };

  const logout = async () => {
    await StorageService.removeToken();
    setUser(null);
  };

  const refreshProfile = async () => {
    await fetchCurrentUser();
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

