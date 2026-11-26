import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  RefreshControl,
  ActivityIndicator,
} from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { RootStackParamList } from "../types/navigation";
import { apiClient } from "../services/api";
import { InterviewSession } from "../types";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Colors } from "../constants/colors";

type Props = NativeStackScreenProps<RootStackParamList, "Analytics">;

export const ProgressAnalyticsScreen: React.FC<Props> = ({ navigation }) => {
  const [sessions, setSessions] = useState<InterviewSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const res = await apiClient.get<InterviewSession[]>("/interviews/history");
      setSessions(res.data);
    } catch {
      // Offline fallback
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const completed = sessions.filter((s) => s.status === "COMPLETED" && s.overall_score != null);
  const totalCount = completed.length;
  const avgScore =
    totalCount > 0
      ? Math.round(completed.reduce((acc, s) => acc + (s.overall_score || 0), 0) / totalCount)
      : 0;
  const highestScore =
    totalCount > 0
      ? Math.round(Math.max(...completed.map((s) => s.overall_score || 0)))
      : 0;

  // Track breakdown
  const getTrackStats = (typePrefix: string) => {
    const matching = completed.filter((s) =>
      s.interview_type.toLowerCase().includes(typePrefix.toLowerCase())
    );
    const count = matching.length;
    const avg =
      count > 0
        ? Math.round(matching.reduce((acc, s) => acc + (s.overall_score || 0), 0) / count)
        : 0;
    return { count, avg };
  };

  const techStats = getTrackStats("Tech");
  const hrStats = getTrackStats("HR");
  const codingStats = getTrackStats("Coding");
  const projectStats = getTrackStats("Project");

  // Performance distribution
  const highScoring = completed.filter((s) => (s.overall_score || 0) >= 70).length;
  const midScoring = completed.filter((s) => (s.overall_score || 0) >= 45 && (s.overall_score || 0) < 70).length;
  const lowScoring = completed.filter((s) => (s.overall_score || 0) < 45).length;

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
      <Text style={styles.screenTitle}>Placement Progress Analytics</Text>
      <Text style={styles.screenSubtitle}>
        Calculated directly from your stored interview simulations and rubric evaluations.
      </Text>

      {/* Hero Performance Overview */}
      <Card style={styles.heroCard}>
        <Text style={styles.cardHeader}>Overall Readiness</Text>
        <View style={styles.statsRow}>
          <View style={styles.statBox}>
            <Text style={[styles.statValue, { color: Colors.primary }]}>
              {avgScore > 0 ? `${avgScore}%` : "—"}
            </Text>
            <Text style={styles.statLabel}>Average Score</Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.statBox}>
            <Text style={[styles.statValue, { color: Colors.success }]}>
              {highestScore > 0 ? `${highestScore}%` : "—"}
            </Text>
            <Text style={styles.statLabel}>Highest Score</Text>
          </View>
          <View style={styles.divider} />
          <View style={styles.statBox}>
            <Text style={styles.statValue}>{totalCount}</Text>
            <Text style={styles.statLabel}>Completed</Text>
          </View>
        </View>
      </Card>

      {/* Track Mastery Breakdown */}
      <Text style={styles.sectionTitle}>Track Performance Breakdown</Text>
      <Card style={styles.breakdownCard}>
        {[
          { label: "Technical Concepts", stats: techStats, emoji: "💻" },
          { label: "HR & Behavioral", stats: hrStats, emoji: "🤝" },
          { label: "Live Coding", stats: codingStats, emoji: "⚡" },
          { label: "System & Project", stats: projectStats, emoji: "📁" },
        ].map((track, i) => (
          <View key={i}>
            <View style={styles.trackRow}>
              <View style={styles.trackInfo}>
                <Text style={styles.trackEmoji}>{track.emoji}</Text>
                <View>
                  <Text style={styles.trackName}>{track.label}</Text>
                  <Text style={styles.trackCount}>{track.stats.count} sessions completed</Text>
                </View>
              </View>
              <Text
                style={[
                  styles.trackScore,
                  track.stats.avg >= 70
                    ? { color: Colors.success }
                    : track.stats.avg >= 45
                    ? { color: Colors.warning }
                    : { color: Colors.textMuted },
                ]}
              >
                {track.stats.count > 0 ? `${track.stats.avg}%` : "No Data"}
              </Text>
            </View>
            {i < 3 && <View style={styles.itemDivider} />}
          </View>
        ))}
      </Card>

      {/* Score Readiness Distribution */}
      <Text style={styles.sectionTitle}>Readiness Distribution</Text>
      <Card style={styles.distributionCard}>
        <View style={styles.distRow}>
          <Text style={styles.distLabel}>🟢 Placement Ready (≥70%)</Text>
          <Text style={styles.distValue}>{highScoring} sessions</Text>
        </View>
        <View style={styles.distRow}>
          <Text style={styles.distLabel}>🟡 Needs Polish (45-69%)</Text>
          <Text style={styles.distValue}>{midScoring} sessions</Text>
        </View>
        <View style={styles.distRow}>
          <Text style={styles.distLabel}>🔴 Needs Practice (&lt;45%)</Text>
          <Text style={styles.distValue}>{lowScoring} sessions</Text>
        </View>
      </Card>

      {/* Action Recommendation */}
      <Card style={styles.recommendationCard}>
        <Text style={styles.recTitle}>🎯 Recommended Next Step</Text>
        <Text style={styles.recBody}>
          {totalCount === 0
            ? "Take your first mock interview simulation to populate baseline performance metrics."
            : avgScore < 60
            ? "Target foundational technical concepts with a 3-question session to build core confidence."
            : "Practice Intermediate and Advanced questions to test edge cases, system trade-offs, and behavioral depth."}
        </Text>
        <Button
          title="⚡ Start Practice Simulation"
          onPress={() => navigation.navigate("SetupInterview")}
          style={styles.recButton}
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
  heroCard: {
    padding: 18,
    marginBottom: 16,
  },
  cardHeader: {
    fontSize: 14,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 12,
  },
  statsRow: {
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
  },
  statBox: {
    flex: 1,
    alignItems: "center",
  },
  statValue: {
    fontSize: 24,
    fontWeight: "800",
    color: Colors.textPrimary,
  },
  statLabel: {
    fontSize: 11,
    color: Colors.textSecondary,
    marginTop: 4,
  },
  divider: {
    width: 1,
    height: 36,
    backgroundColor: Colors.border,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 10,
    marginTop: 6,
  },
  breakdownCard: {
    padding: 16,
    marginBottom: 16,
  },
  trackRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 8,
  },
  trackInfo: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  trackEmoji: {
    fontSize: 22,
  },
  trackName: {
    fontSize: 14,
    fontWeight: "600",
    color: Colors.textPrimary,
  },
  trackCount: {
    fontSize: 11,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  trackScore: {
    fontSize: 16,
    fontWeight: "700",
  },
  itemDivider: {
    height: 1,
    backgroundColor: Colors.border,
    marginVertical: 4,
  },
  distributionCard: {
    padding: 16,
    marginBottom: 16,
  },
  distRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 8,
  },
  distLabel: {
    fontSize: 13,
    color: Colors.textPrimary,
  },
  distValue: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.textSecondary,
  },
  recommendationCard: {
    padding: 18,
    marginBottom: 16,
    backgroundColor: "#EEF2FF",
    borderColor: "#C7D2FE",
  },
  recTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: Colors.primary,
    marginBottom: 6,
  },
  recBody: {
    fontSize: 13,
    color: Colors.textPrimary,
    lineHeight: 19,
    marginBottom: 12,
  },
  recButton: {
    marginTop: 4,
  },
});

