import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert,
  TouchableOpacity,
} from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { RootStackParamList } from "../types/navigation";
import { useAuth } from "../context/AuthContext";
import { apiClient } from "../services/api";
import { Card } from "../components/Card";
import { Input } from "../components/Input";
import { Button } from "../components/Button";
import { Colors } from "../constants/colors";

type Props = NativeStackScreenProps<RootStackParamList, "Profile">;

export const ProfileSettingsScreen: React.FC<Props> = ({ navigation }) => {
  const { user, refreshProfile, logout } = useAuth();

  const [targetRole, setTargetRole] = useState(user?.profile?.target_role || "Software Engineer");
  const [experienceLevel, setExperienceLevel] = useState(user?.profile?.experience_level || "Fresher");
  const [education, setEducation] = useState(user?.profile?.education || "MCA / Computer Science");
  const [saving, setSaving] = useState(false);

  const handleSaveProfile = async () => {
    try {
      setSaving(true);
      await apiClient.put("/profile", {
        target_role: targetRole.trim(),
        experience_level: experienceLevel,
        education: education.trim(),
      });
      await refreshProfile();
      Alert.alert("Success", "Profile updated successfully.");
    } catch (err: any) {
      Alert.alert("Error", err.message || "Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.scrollContent}
      nestedScrollEnabled={true}
      showsVerticalScrollIndicator={true}
    >
      <Text style={styles.screenTitle}>Candidate Profile & Settings</Text>
      <Text style={styles.screenSubtitle}>
        Manage your default target role, experience tier, and account settings.
      </Text>

      {/* Account Info */}
      <Card style={styles.card}>
        <Text style={styles.sectionHeader}>Account Information</Text>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Full Name</Text>
          <Text style={styles.infoValue}>{user?.full_name || "Student Candidate"}</Text>
        </View>
        <View style={styles.divider} />
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Email Address</Text>
          <Text style={styles.infoValue}>{user?.email || "candidate@test.com"}</Text>
        </View>
      </Card>

      {/* Target Role & Level */}
      <Card style={styles.card}>
        <Text style={styles.sectionHeader}>Career & Target Preferences</Text>

        <Text style={styles.inputLabel}>Target Job Role</Text>
        <Input
          placeholder="e.g. Python Backend Developer, React Native Engineer"
          value={targetRole}
          onChangeText={setTargetRole}
          containerStyle={styles.inputField}
        />

        <Text style={styles.inputLabel}>Education Background</Text>
        <Input
          placeholder="e.g. MCA, B.Tech CSE, BCA"
          value={education}
          onChangeText={setEducation}
          containerStyle={styles.inputField}
        />

        <Text style={styles.inputLabel}>Experience Tier</Text>
        <View style={styles.pillRow}>
          {["Fresher", "Intermediate", "Advanced"].map((level) => (
            <TouchableOpacity
              key={level}
              style={[
                styles.pillButton,
                experienceLevel === level && styles.pillButtonSelected,
              ]}
              onPress={() => setExperienceLevel(level)}
            >
              <Text
                style={[
                  styles.pillText,
                  experienceLevel === level && styles.pillTextSelected,
                ]}
              >
                {level}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Button
          title={saving ? "Saving Changes..." : "Save Profile Preferences"}
          onPress={handleSaveProfile}
          loading={saving}
          style={styles.saveButton}
        />
      </Card>

      {/* Sign Out Card */}
      <Card style={styles.card}>
        <Text style={styles.sectionHeader}>Session Management</Text>
        <Text style={styles.sessionDesc}>
          Signing out will safely clear your active session token from secure storage.
        </Text>
        <Button
          title="Sign Out of InterviewIQ"
          variant="outline"
          onPress={logout}
          style={styles.logoutButton}
        />
      </Card>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 20,
    paddingBottom: 80,
  },
  screenTitle: {
    fontSize: 20,
    fontWeight: "800",
    color: Colors.textPrimary,
    marginBottom: 4,
  },
  screenSubtitle: {
    fontSize: 13,
    color: Colors.textSecondary,
    marginBottom: 16,
    lineHeight: 18,
  },
  card: {
    padding: 18,
    marginBottom: 16,
  },
  sectionHeader: {
    fontSize: 15,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 6,
  },
  infoLabel: {
    fontSize: 13,
    color: Colors.textSecondary,
  },
  infoValue: {
    fontSize: 14,
    fontWeight: "600",
    color: Colors.textPrimary,
  },
  divider: {
    height: 1,
    backgroundColor: Colors.border,
    marginVertical: 8,
  },
  inputLabel: {
    fontSize: 13,
    fontWeight: "600",
    color: Colors.textSecondary,
    marginBottom: 6,
    marginTop: 6,
  },
  inputField: {
    marginBottom: 10,
  },
  pillRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 16,
    marginTop: 4,
  },
  pillButton: {
    flex: 1,
    paddingVertical: 10,
    alignItems: "center",
    borderRadius: 10,
    borderWidth: 1.5,
    borderColor: Colors.border,
    marginHorizontal: 3,
    backgroundColor: Colors.surface,
  },
  pillButtonSelected: {
    borderColor: Colors.primary,
    backgroundColor: Colors.primary,
  },
  pillText: {
    fontSize: 12,
    fontWeight: "600",
    color: Colors.textSecondary,
  },
  pillTextSelected: {
    color: Colors.textInverse,
  },
  saveButton: {
    marginTop: 6,
  },
  sessionDesc: {
    fontSize: 13,
    color: Colors.textSecondary,
    lineHeight: 18,
    marginBottom: 12,
  },
  logoutButton: {
    borderColor: Colors.danger,
  },
});
