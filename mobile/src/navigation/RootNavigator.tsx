import React from "react";
import { View, ActivityIndicator, StyleSheet } from "react-native";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { RootStackParamList } from "../types/navigation";
import { useAuth } from "../context/AuthContext";
import { Colors } from "../constants/colors";

// Screen Imports
import { LoginScreen } from "../screens/LoginScreen";
import { RegisterScreen } from "../screens/RegisterScreen";
import { DashboardScreen } from "../screens/DashboardScreen";
import { SetupInterviewScreen } from "../screens/SetupInterviewScreen";
import { ActiveInterviewScreen } from "../screens/ActiveInterviewScreen";
import { ResultsScreen } from "../screens/ResultsScreen";
import { HistoryScreen } from "../screens/HistoryScreen";
import { ProgressAnalyticsScreen } from "../screens/ProgressAnalyticsScreen";
import { ProfileSettingsScreen } from "../screens/ProfileSettingsScreen";

const Stack = createNativeStackNavigator<RootStackParamList>();

export const RootNavigator: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={Colors.primary} />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: Colors.card,
          },
          headerTintColor: Colors.textPrimary,
          headerTitleStyle: {
            fontWeight: "700",
          },
          headerShadowVisible: false,
          contentStyle: {
            backgroundColor: Colors.background,
          },
        }}
      >
        {user ? (
          // Authenticated App Flow
          <>
            <Stack.Screen
              name="Dashboard"
              component={DashboardScreen}
              options={{ title: "InterviewIQ AI", headerBackVisible: false }}
            />
            <Stack.Screen
              name="SetupInterview"
              component={SetupInterviewScreen}
              options={{ title: "Configure Session" }}
            />
            <Stack.Screen
              name="ActiveInterview"
              component={ActiveInterviewScreen}
              options={{
                title: "Mock Interview",
                headerBackVisible: false, // Prevent accidental exit mid-interview
              }}
            />
            <Stack.Screen
              name="Results"
              component={ResultsScreen}
              options={{
                title: "Feedback & Evaluation",
                headerBackVisible: false,
              }}
            />
            <Stack.Screen
              name="History"
              component={HistoryScreen}
              options={{ title: "Interview History" }}
            />
            <Stack.Screen
              name="Analytics"
              component={ProgressAnalyticsScreen}
              options={{ title: "Placement Analytics" }}
            />
            <Stack.Screen
              name="Profile"
              component={ProfileSettingsScreen}
              options={{ title: "Profile & Settings" }}
            />
          </>
        ) : (
          // Unauthenticated Auth Flow
          <>
            <Stack.Screen
              name="Login"
              component={LoginScreen}
              options={{ headerShown: false }}
            />
            <Stack.Screen
              name="Register"
              component={RegisterScreen}
              options={{ title: "Create Account" }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: Colors.background,
  },
});

