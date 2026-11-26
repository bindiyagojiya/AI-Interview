import * as SecureStore from "expo-secure-store";
import { Platform } from "react-native";

const TOKEN_KEY = "interviewiq_auth_token";
const USER_KEY = "interviewiq_user_data";

// In-memory fallback for non-native environments (e.g. web preview)
const memoryStore: Record<string, string> = {};

export const StorageService = {
  async saveToken(token: string): Promise<void> {
    try {
      if (Platform.OS === "web") {
        memoryStore[TOKEN_KEY] = token;
      } else {
        await SecureStore.setItemAsync(TOKEN_KEY, token);
      }
    } catch {
      memoryStore[TOKEN_KEY] = token;
    }
  },

  async getToken(): Promise<string | null> {
    try {
      if (Platform.OS === "web") {
        return memoryStore[TOKEN_KEY] || null;
      }
      return await SecureStore.getItemAsync(TOKEN_KEY);
    } catch {
      return memoryStore[TOKEN_KEY] || null;
    }
  },

  async removeToken(): Promise<void> {
    try {
      if (Platform.OS === "web") {
        delete memoryStore[TOKEN_KEY];
      } else {
        await SecureStore.deleteItemAsync(TOKEN_KEY);
      }
    } catch {
      delete memoryStore[TOKEN_KEY];
    }
  },

  async saveUserData(userData: object): Promise<void> {
    const json = JSON.stringify(userData);
    try {
      if (Platform.OS === "web") {
        memoryStore[USER_KEY] = json;
      } else {
        await SecureStore.setItemAsync(USER_KEY, json);
      }
    } catch {
      memoryStore[USER_KEY] = json;
    }
  },

  async getUserData<T>(): Promise<T | null> {
    try {
      let raw: string | null = null;
      if (Platform.OS === "web") {
        raw = memoryStore[USER_KEY] || null;
      } else {
        raw = await SecureStore.getItemAsync(USER_KEY);
      }
      return raw ? (JSON.parse(raw) as T) : null;
    } catch {
      return null;
    }
  },
};

