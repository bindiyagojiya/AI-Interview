// 
import { Platform } from "react-native";

// PC's Wi-Fi IP — use this for a physical phone
export const LOCAL_DEV_IP = "192.168.235.244";

const DEV_API_URL = Platform.select({
  // Android Studio emulator
  android: "http://10.0.2.2:8000/api/v1",

  // iOS simulator
  ios: "http://localhost:8000/api/v1",

  // Web
  default: "http://localhost:8000/api/v1",
});

export const Config = {
  API_BASE_URL: DEV_API_URL,
  TIMEOUT_MS: 15000,
  APP_NAME: "InterviewIQ AI",
};
