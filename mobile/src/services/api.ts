import axios from "axios";
import { Config } from "../constants/config";
import { StorageService } from "./storage";

export const apiClient = axios.create({
  baseURL: Config.API_BASE_URL,
  timeout: Config.TIMEOUT_MS,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request Interceptor: Attach JWT Bearer Token
apiClient.interceptors.request.use(
  async (config) => {
    const token = await StorageService.getToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Uniform error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token on unauthorized
      StorageService.removeToken();
    }
    const message =
      error.response?.data?.detail ||
      error.message ||
      "Unable to communicate with the server.";
    return Promise.reject(new Error(message));
  }
);

