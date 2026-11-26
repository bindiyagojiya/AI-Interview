import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  RefreshControl,
  TouchableOpacity,
} from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { RootStackParamList } from "../types/navigation";
import { apiClient } from "../services/api";
import { InterviewSession } from "../types";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Colors } from "../constants/colors";

type Props = NativeStackScreenProps<RootStackParamList, "History">;

export const HistoryScreen: React.FC<Props> = ({ navigation }) => {
  const [sessions, setSessions] = useState<InterviewSession[]>([]);
  const [filter, setFilter] = useState<"All" | "Technical" | "HR">("All");
  const [refreshing, setRefreshing] = useState(false);

  const fetchHistory = async () => {
    try {
      setRefreshing(true);
      const response = await apiClient.get<InterviewSession[]>("/interviews/history");
      setSessions(response.data);
    } catch {
      // Graceful offline fallback
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const filteredSessions = sessions.filter((s) => {
    if (filter === "All") return true;
    return s.interview_type.toLowerCase() === filter.toLowerCase();
  });

  const renderItem = ({ item }: { item: InterviewSession }) => {
    const isCompleted = item.status === "COMPLETED";
    const score = item.overall_score || 0;
    const badgeColor =
      score >= 70 ? Colors.success : score >= 45 ? Colors.warning : Colors.danger;

    return (
      <TouchableOpacity
        activeOpacity={0.7}
        onPress={() =>
          navigation.navigate("Results", {
            sessionId: item.id,
            overallScore: item.overall_score || 0,
            answersCount: item.num_questions || 5,
          })
        }
      >
        <Card style={styles.card}>
          <View style={styles.cardHeader}>
            <View style={{ flex: 1, marginRight: 12 }}>
              <Text style={styles.roleTitle}>{item.target_role}</Text>
              <Text style={styles.metaText}>
                {item.interview_type} • {item.difficulty} •{" "}
                {new Date(item.created_at).toLocaleDateString()}
              </Text>
              <Text style={styles.viewDetailsHint}>
                Tap to review answers & feedback →
              </Text>
            </View>
            <View
              style={[
                styles.scoreBadge,
                { backgroundColor: isCompleted ? badgeColor : Colors.textMuted },
              ]}
            >
              <Text style={styles.scoreText}>
                {isCompleted ? `${score}%` : "Incomplete"}
              </Text>
            </View>
          </View>
        </Card>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      {/* Category Filter Pills */}
      <View style={styles.filterBar}>
        {(["All", "Technical", "HR"] as const).map((cat) => (
          <TouchableOpacity
            key={cat}
            style={[
              styles.filterPill,
              filter === cat && styles.filterPillSelected,
            ]}
            onPress={() => setFilter(cat)}
          >
            <Text
              style={[
                styles.filterText,
                filter === cat && styles.filterTextSelected,
              ]}
            >
              {cat}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <FlatList
        data={filteredSessions}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={fetchHistory}
            colors={[Colors.primary]}
          />
        }
        ListEmptyComponent={
          <Card style={styles.emptyCard}>
            <Text style={styles.emptyTitle}>No past interviews found</Text>
            <Text style={styles.emptySubtitle}>
              Complete an interview session to see your historical scores and progression here.
            </Text>
            <Button
              title="Start an Interview Now"
              onPress={() => navigation.navigate("SetupInterview")}
              style={styles.emptyButton}
            />
          </Card>
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  filterBar: {
    flexDirection: "row",
    paddingHorizontal: 20,
    paddingVertical: 12,
    backgroundColor: Colors.card,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  filterPill: {
    paddingVertical: 6,
    paddingHorizontal: 16,
    borderRadius: 20,
    backgroundColor: Colors.surface,
    marginRight: 8,
  },
  filterPillSelected: {
    backgroundColor: Colors.primary,
  },
  filterText: {
    fontSize: 13,
    fontWeight: "600",
    color: Colors.textSecondary,
  },
  filterTextSelected: {
    color: Colors.textInverse,
  },
  listContent: {
    padding: 20,
  },
  card: {
    padding: 18,
    marginVertical: 6,
  },
  viewDetailsHint: {
    fontSize: 12,
    color: Colors.primary,
    marginTop: 6,
    fontWeight: "500",
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  roleTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  metaText: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 4,
  },
  scoreBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  scoreText: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.textInverse,
  },
  emptyCard: {
    alignItems: "center",
    padding: 28,
    marginTop: 40,
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 6,
  },
  emptySubtitle: {
    fontSize: 13,
    color: Colors.textSecondary,
    textAlign: "center",
    marginBottom: 18,
    lineHeight: 18,
  },
  emptyButton: {
    width: "100%",
  },
});

