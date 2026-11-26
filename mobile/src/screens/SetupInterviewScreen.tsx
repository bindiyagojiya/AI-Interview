import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { RootStackParamList } from "../types/navigation";
import { apiClient } from "../services/api";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Input } from "../components/Input";
import { Colors } from "../constants/colors";
import { InterviewSession } from "../types";

type Props = NativeStackScreenProps<RootStackParamList, "SetupInterview">;

export const SetupInterviewScreen: React.FC<Props> = ({ route, navigation }) => {
  const prefill = route?.params;

  const [interviewType, setInterviewType] = useState<"Technical" | "HR" | "Coding" | "Project-Based">(
    prefill?.prefillTrack || "Technical"
  );
  const [targetRole, setTargetRole] = useState(
    prefill?.prefillRole || "Python Backend Developer"
  );
  const [difficulty, setDifficulty] = useState<"Fresher" | "Intermediate" | "Advanced">(
    prefill?.prefillDifficulty || "Fresher"
  );
  const [numQuestions, setNumQuestions] = useState(prefill?.prefillTopics ? 3 : 5);
  const [topics, setTopics] = useState(prefill?.prefillTopics || "");
  const [loading, setLoading] = useState(false);

  const handleStartInterview = async () => {
    if (!targetRole.trim()) {
      Alert.alert("Missing Role", "Please enter your target role.");
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.post<InterviewSession>("/interviews/start", {
        interview_type: interviewType,
        target_role: targetRole.trim(),
        difficulty: difficulty,
        num_questions: numQuestions,
        topics: topics.trim() || undefined,
      });

      navigation.replace("ActiveInterview", {
        sessionId: response.data.id,
        interviewType: interviewType,
        targetRole: targetRole.trim(),
        difficulty: difficulty,
        numQuestions: numQuestions,
      });
    } catch (err: any) {
      Alert.alert("Failed to Start", err.message || "Could not initialize interview session.");
    } finally {
      setLoading(false);
    }
  };

  const TRACKS: { key: "Technical" | "HR" | "Coding" | "Project-Based"; label: string; emoji: string }[] = [
    { key: "Technical", label: "Technical", emoji: "💻" },
    { key: "HR", label: "Behavioral", emoji: "🤝" },
    { key: "Coding", label: "Live Coding", emoji: "⚡" },
    { key: "Project-Based", label: "Project & System", emoji: "📁" },
  ];

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.scrollContent}
      nestedScrollEnabled={true}
      showsVerticalScrollIndicator={true}
      keyboardShouldPersistTaps="handled"
    >
      <Text style={styles.title}>Configure Interview</Text>
      <Text style={styles.subtitle}>
        Customize your mock interview parameters to simulate real-world hiring rounds.
      </Text>

      {/* 1. Track Selector */}
      <Card style={styles.sectionCard}>
        <Text style={styles.sectionLabel}>1. Select Interview Category</Text>
        <View style={styles.typeGrid}>
          {TRACKS.map((t) => (
            <TouchableOpacity
              key={t.key}
              style={[
                styles.typeGridButton,
                interviewType === t.key && styles.typeButtonSelected,
              ]}
              onPress={() => setInterviewType(t.key)}
            >
              <Text style={styles.typeEmoji}>{t.emoji}</Text>
              <Text
                style={[
                  styles.typeButtonText,
                  interviewType === t.key && styles.typeButtonTextSelected,
                ]}
              >
                {t.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </Card>

      {/* 2. Target Job Role */}
      <Card style={styles.sectionCard}>
        <Text style={styles.sectionLabel}>2. Target Job Role</Text>
        <Input
          placeholder="e.g. Python Developer, React Developer, DevOps..."
          value={targetRole}
          onChangeText={setTargetRole}
          containerStyle={styles.roleInput}
        />
        <View style={styles.roleSuggestionsRow}>
          {["Python", "React", "Java", "SQL", "Data Science", "DevOps"].map((role) => (
            <TouchableOpacity
              key={role}
              style={[
                styles.suggestionPill,
                targetRole.toLowerCase().includes(role.toLowerCase().split(" ")[0]) && styles.suggestionPillSelected,
              ]}
              onPress={() => setTargetRole(`${role} Developer`)}
            >
              <Text
                style={[
                  styles.suggestionPillText,
                  targetRole.toLowerCase().includes(role.toLowerCase().split(" ")[0]) && styles.suggestionPillTextSelected,
                ]}
              >
                {role}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </Card>

      {/* 3. Difficulty Level */}
      <Card style={styles.sectionCard}>
        <Text style={styles.sectionLabel}>3. Experience Level</Text>
        <View style={styles.pillRow}>
          {(["Fresher", "Intermediate", "Advanced"] as const).map((level) => (
            <TouchableOpacity
              key={level}
              style={[
                styles.pillButton,
                difficulty === level && styles.pillButtonSelected,
              ]}
              onPress={() => setDifficulty(level)}
            >
              <Text
                style={[
                  styles.pillText,
                  difficulty === level && styles.pillTextSelected,
                ]}
              >
                {level}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </Card>

      {/* 4. Question Count */}
      <Card style={styles.sectionCard}>
        <Text style={styles.sectionLabel}>4. Session Length</Text>
        <View style={styles.pillRow}>
          {[3, 5, 10].map((count) => (
            <TouchableOpacity
              key={count}
              style={[
                styles.pillButton,
                numQuestions === count && styles.pillButtonSelected,
              ]}
              onPress={() => setNumQuestions(count)}
            >
              <Text
                style={[
                  styles.pillText,
                  numQuestions === count && styles.pillTextSelected,
                ]}
              >
                {count} Questions
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </Card>

      {/* 5. Optional Technical Topics */}
      <Card style={styles.sectionCard}>
        <Text style={styles.sectionLabel}>5. Focus Topics (Optional)</Text>
        <Input
          placeholder="e.g. React Hooks, Redux, Docker, Joins, Concurrency..."
          value={topics}
          onChangeText={setTopics}
          containerStyle={styles.roleInput}
        />
      </Card>

      <Button
        title="Begin Interview Simulation →"
        onPress={handleStartInterview}
        loading={loading}
        style={styles.startButton}
      />
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
  title: {
    fontSize: 24,
    fontWeight: "800",
    color: Colors.textPrimary,
    marginBottom: 6,
  },
  subtitle: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginBottom: 20,
    lineHeight: 20,
  },
  sectionCard: {
    padding: 18,
    marginBottom: 16,
  },
  sectionLabel: {
    fontSize: 15,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 14,
  },
  typeGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    gap: 8,
  },
  typeGridButton: {
    width: "48%",
    alignItems: "center",
    padding: 14,
    borderRadius: 12,
    borderWidth: 1.5,
    borderColor: Colors.border,
    backgroundColor: Colors.surface,
  },
  typeButtonSelected: {
    borderColor: Colors.primary,
    backgroundColor: "#EEF2FF",
  },
  typeEmoji: {
    fontSize: 24,
    marginBottom: 6,
  },
  typeButtonText: {
    fontSize: 14,
    fontWeight: "600",
    color: Colors.textSecondary,
  },
  typeButtonTextSelected: {
    color: Colors.primary,
    fontWeight: "700",
  },
  roleInput: {
    marginBottom: 0,
  },
  roleSuggestionsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginTop: 10,
    gap: 6,
  },
  suggestionPill: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: Colors.border,
    backgroundColor: Colors.surface,
  },
  suggestionPillSelected: {
    borderColor: Colors.primary,
    backgroundColor: "#EEF2FF",
  },
  suggestionPillText: {
    fontSize: 12,
    fontWeight: "500",
    color: Colors.textSecondary,
  },
  suggestionPillTextSelected: {
    color: Colors.primary,
    fontWeight: "700",
  },
  pillRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  pillButton: {
    flex: 1,
    paddingVertical: 12,
    alignItems: "center",
    borderRadius: 10,
    borderWidth: 1.5,
    borderColor: Colors.border,
    marginHorizontal: 4,
    backgroundColor: Colors.surface,
  },
  pillButtonSelected: {
    borderColor: Colors.primary,
    backgroundColor: Colors.primary,
  },
  pillText: {
    fontSize: 13,
    fontWeight: "600",
    color: Colors.textSecondary,
  },
  pillTextSelected: {
    color: Colors.textInverse,
  },
  startButton: {
    marginTop: 12,
    marginBottom: 20,
  },
});
