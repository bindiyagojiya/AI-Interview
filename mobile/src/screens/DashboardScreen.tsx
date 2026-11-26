import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
} from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { RootStackParamList } from "../types/navigation";
import { useAuth } from "../context/AuthContext";
import { apiClient } from "../services/api";
import { InterviewSession, PracticeRecommendations } from "../types";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Colors } from "../constants/colors";

type Props = NativeStackScreenProps<RootStackParamList, "Dashboard">;

export const DashboardScreen: React.FC<Props> = ({ navigation }) => {
  const { user, logout } = useAuth();
  const [recentInterviews, setRecentInterviews] = useState<InterviewSession[]>([]);
  const [recommendations, setRecommendations] = useState<PracticeRecommendations | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    totalCompleted: 0,
    averageScore: 0,
  });

  const loadDashboardData = async () => {
    try {
      const [historyRes, recsRes] = await Promise.all([
        apiClient.get<InterviewSession[]>("/interviews/history"),
        apiClient.get<PracticeRecommendations>("/interviews/recommendations"),
      ]);
      const sessions = historyRes.data;
      setRecentInterviews(sessions.slice(0, 3));
      setRecommendations(recsRes.data);

      const completed = sessions.filter((s) => s.status === "COMPLETED" && s.overall_score != null);
      const avg =
        completed.length > 0
          ? Math.round(
              completed.reduce((sum, s) => sum + (s.overall_score || 0), 0) /
                completed.length
            )
          : 0;

      setStats({
        totalCompleted: completed.length,
        averageScore: avg,
      });
    } catch {
      // Gracefully handle offline or network delay
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboardData();
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.scrollContent}
      nestedScrollEnabled={true}
      showsVerticalScrollIndicator={true}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[Colors.primary]} />
      }
    >
      {/* Header Profile Bar */}
      <View style={styles.headerRow}>
        <View style={{ flex: 1, marginRight: 8 }}>
          <Text style={styles.greeting}>Hello, {user?.full_name || "Student"} 👋</Text>
          <Text style={styles.targetRole}>
            {user?.profile?.target_role || "Software Engineer Candidate"}
          </Text>
        </View>
        <TouchableOpacity
          style={styles.profileBadgeButton}
          onPress={() => navigation.navigate("Profile")}
        >
          <Text style={styles.profileBadgeText}>⚙️ Profile</Text>
        </TouchableOpacity>
      </View>

      {/* Main Readiness Gauge Card */}
      <Card style={styles.statsHeroCard}>
        <Text style={styles.heroTitle}>Placement Readiness</Text>
        <View style={styles.heroGaugeRow}>
          <View style={styles.gaugeContainer}>
            <Text style={styles.gaugeNumber}>
              {stats.averageScore > 0 ? `${stats.averageScore}%` : "N/A"}
            </Text>
            <Text style={styles.gaugeLabel}>Average Score</Text>
          </View>
          <View style={styles.verticalDivider} />
          <View style={styles.gaugeContainer}>
            <Text style={styles.gaugeNumber}>{stats.totalCompleted}</Text>
            <Text style={styles.gaugeLabel}>Sessions Finished</Text>
          </View>
        </View>
        <Button
          title="⚡ Start New Mock Interview"
          onPress={() => navigation.navigate("SetupInterview")}
          style={styles.heroButton}
        />
        <View style={styles.quickNavRow}>
          <TouchableOpacity
            style={styles.quickNavLink}
            onPress={() => navigation.navigate("Analytics")}
          >
            <Text style={styles.quickNavText}>📊 View Analytics Trend →</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.quickNavLink}
            onPress={() => navigation.navigate("History")}
          >
            <Text style={styles.quickNavText}>🕒 Past History →</Text>
          </TouchableOpacity>
        </View>
      </Card>

      {/* Personalized Practice Plan based on Stored Concept Gaps */}
      {recommendations && recommendations.weak_topics.length > 0 ? (
        <Card style={styles.planCard}>
          <View style={styles.planHeaderRow}>
            <Text style={styles.planTitle}>🎯 Focus Area Recommendations</Text>
            <Text style={styles.planBadge}>Based on Stored Data</Text>
          </View>
          <Text style={styles.planAdvice}>{recommendations.actionable_advice}</Text>
          <View style={styles.planChipsRow}>
            {recommendations.weak_topics.map((topic, i) => (
              <View key={i} style={styles.planChip}>
                <Text style={styles.planChipText}>{topic}</Text>
              </View>
            ))}
          </View>
          <Button
            title={`⚡ Practice Weak Topics (${recommendations.weak_topics.slice(0, 2).join(", ")})`}
            onPress={() =>
              navigation.navigate("SetupInterview", {
                prefillTrack: (recommendations.lowest_scoring_track as any) || "Technical",
                prefillRole: recommendations.recommended_role,
                prefillDifficulty: (recommendations.recommended_difficulty as any) || "Fresher",
                prefillTopics: recommendations.weak_topics.slice(0, 4).join(", "),
              })
            }
            style={styles.planButton}
          />
        </Card>
      ) : null}

      {/* Recommended Practice Tracks */}
      <Text style={styles.sectionTitle}>Practice Tracks</Text>
      <View style={styles.tracksRow}>
        <TouchableOpacity
          style={[styles.trackCard, { borderColor: Colors.primary }]}
          onPress={() => navigation.navigate("SetupInterview")}
          activeOpacity={0.8}
        >
          <Text style={styles.trackEmoji}>💻</Text>
          <Text style={styles.trackTitle}>Technical</Text>
          <Text style={styles.trackSubtitle}>Python, SQL, DSA & System Design</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.trackCard, { borderColor: Colors.accent }]}
          onPress={() => navigation.navigate("SetupInterview")}
          activeOpacity={0.8}
        >
          <Text style={styles.trackEmoji}>🤝</Text>
          <Text style={styles.trackTitle}>HR & Behavioral</Text>
          <Text style={styles.trackSubtitle}>STAR Method, Teamwork, Scenario</Text>
        </TouchableOpacity>
      </View>

      {/* Recent Attempts */}
      <View style={styles.sectionHeaderRow}>
        <Text style={styles.sectionTitle}>Recent Attempts</Text>
        {recentInterviews.length > 0 && (
          <TouchableOpacity onPress={() => navigation.navigate("History")}>
            <Text style={styles.viewAllText}>View All →</Text>
          </TouchableOpacity>
        )}
      </View>

      {recentInterviews.length === 0 ? (
        <Card style={styles.emptyCard}>
          <Text style={styles.emptyEmoji}>🎯</Text>
          <Text style={styles.emptyTitle}>No interviews yet</Text>
          <Text style={styles.emptySubtitle}>
            Take your first mock interview to get detailed AI rubric feedback.
          </Text>
          <Button
            title="Start First Session"
            variant="outline"
            onPress={() => navigation.navigate("SetupInterview")}
            style={styles.emptyButton}
          />
        </Card>
      ) : (
        recentInterviews.map((item) => (
          <TouchableOpacity
            key={item.id}
            activeOpacity={0.7}
            onPress={() =>
              navigation.navigate("Results", {
                sessionId: item.id,
                overallScore: item.overall_score || 0,
                answersCount: item.num_questions || 5,
              })
            }
          >
            <Card style={styles.attemptCard}>
              <View style={styles.attemptTop}>
                <View>
                  <Text style={styles.attemptType}>
                    {item.interview_type} • {item.difficulty}
                  </Text>
                  <Text style={styles.attemptDate}>
                    {new Date(item.created_at).toLocaleDateString()}
                  </Text>
                </View>
                <View
                  style={[
                    styles.scoreBadge,
                    {
                      backgroundColor:
                        (item.overall_score || 0) >= 70
                          ? Colors.success
                          : (item.overall_score || 0) >= 40
                          ? Colors.warning
                          : Colors.danger,
                    },
                  ]}
                >
                  <Text style={styles.scoreBadgeText}>
                    {item.overall_score != null ? `${item.overall_score}%` : "Incomplete"}
                  </Text>
                </View>
              </View>
            </Card>
          </TouchableOpacity>
        ))
      )}
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
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 20,
    marginTop: 10,
  },
  greeting: {
    fontSize: 22,
    fontWeight: "800",
    color: Colors.textPrimary,
  },
  targetRole: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  logoutButton: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 8,
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  logoutText: {
    fontSize: 12,
    fontWeight: "600",
    color: Colors.textSecondary,
  },
  profileBadgeButton: {
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 20,
    backgroundColor: Colors.surface,
    borderWidth: 1.5,
    borderColor: Colors.border,
  },
  profileBadgeText: {
    fontSize: 13,
    fontWeight: "600",
    color: Colors.textPrimary,
  },
  statsHeroCard: {
    backgroundColor: Colors.primaryDark,
    borderColor: Colors.primaryDark,
    padding: 22,
    marginBottom: 24,
  },
  quickNavRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 14,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: "rgba(255, 255, 255, 0.15)",
  },
  quickNavLink: {
    paddingVertical: 4,
  },
  quickNavText: {
    fontSize: 12,
    fontWeight: "600",
    color: Colors.primaryLight,
  },
  planCard: {
    padding: 18,
    marginBottom: 20,
    backgroundColor: "#EFF6FF",
    borderWidth: 1.5,
    borderColor: "#BFDBFE",
  },
  planHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  planTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#1E40AF",
  },
  planBadge: {
    fontSize: 10,
    fontWeight: "700",
    color: "#1D4ED8",
    backgroundColor: "#DBEAFE",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
    textTransform: "uppercase",
  },
  planAdvice: {
    fontSize: 13,
    color: "#1E3A8A",
    lineHeight: 18,
    marginBottom: 10,
  },
  planChipsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginBottom: 12,
  },
  planChip: {
    backgroundColor: "#DBEAFE",
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
  },
  planChipText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#1D4ED8",
  },
  planButton: {
    marginTop: 2,
  },
  heroTitle: {
    fontSize: 14,
    fontWeight: "600",
    color: Colors.primaryLight,
    textTransform: "uppercase",
    letterSpacing: 1,
    marginBottom: 16,
  },
  heroGaugeRow: {
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
    marginBottom: 20,
  },
  gaugeContainer: {
    alignItems: "center",
  },
  gaugeNumber: {
    fontSize: 32,
    fontWeight: "800",
    color: Colors.textInverse,
  },
  gaugeLabel: {
    fontSize: 12,
    color: Colors.primaryLight,
    marginTop: 4,
  },
  verticalDivider: {
    width: 1,
    height: 40,
    backgroundColor: "rgba(255, 255, 255, 0.2)",
  },
  heroButton: {
    backgroundColor: Colors.accent,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 12,
  },
  tracksRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 24,
  },
  trackCard: {
    flex: 1,
    backgroundColor: Colors.card,
    borderRadius: 14,
    padding: 16,
    marginHorizontal: 4,
    borderWidth: 1.5,
  },
  trackEmoji: {
    fontSize: 28,
    marginBottom: 8,
  },
  trackTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 4,
  },
  trackSubtitle: {
    fontSize: 12,
    color: Colors.textSecondary,
    lineHeight: 16,
  },
  sectionHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  viewAllText: {
    fontSize: 14,
    fontWeight: "600",
    color: Colors.primary,
  },
  emptyCard: {
    alignItems: "center",
    padding: 28,
  },
  emptyEmoji: {
    fontSize: 36,
    marginBottom: 8,
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 4,
  },
  emptySubtitle: {
    fontSize: 13,
    color: Colors.textSecondary,
    textAlign: "center",
    marginBottom: 16,
    lineHeight: 18,
  },
  emptyButton: {
    width: "100%",
  },
  attemptCard: {
    padding: 16,
    marginVertical: 6,
  },
  attemptTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  attemptType: {
    fontSize: 15,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  attemptDate: {
    fontSize: 12,
    color: Colors.textMuted,
    marginTop: 2,
  },
  scoreBadge: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 20,
  },
  scoreBadgeText: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.textInverse,
  },
});
