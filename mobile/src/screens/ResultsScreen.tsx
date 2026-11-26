import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { RootStackParamList } from "../types/navigation";
import { apiClient } from "../services/api";
import { InterviewSessionDetail, AnswerDetail } from "../types";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Colors } from "../constants/colors";

type Props = NativeStackScreenProps<RootStackParamList, "Results">;

export const ResultsScreen: React.FC<Props> = ({ route, navigation }) => {
  const { sessionId, overallScore, answersCount, latestEvaluation } = route.params;

  const [sessionDetails, setSessionDetails] = useState<InterviewSessionDetail | null>(null);
  const [loadingDetails, setLoadingDetails] = useState(true);
  const [selectedQuestionIndex, setSelectedQuestionIndex] = useState(0);

  useEffect(() => {
    const fetchSessionReport = async () => {
      try {
        setLoadingDetails(true);
        const response = await apiClient.get<InterviewSessionDetail>(
          `/interviews/${sessionId}/details`
        );
        setSessionDetails(response.data);
      } catch {
        // Graceful offline fallback
      } finally {
        setLoadingDetails(false);
      }
    };

    fetchSessionReport();
  }, [sessionId]);

  const effectiveScore = sessionDetails?.overall_score ?? overallScore ?? 0;
  const answers: AnswerDetail[] = sessionDetails?.answers || [];

  const getScoreColor = (score: number) => {
    if (score >= 70) return Colors.success;
    if (score >= 45) return Colors.warning;
    return Colors.danger;
  };

  // Aggregated session statistics
  const avgCorrectness =
    answers.length > 0
      ? Math.round(answers.reduce((acc, a) => acc + (a.correctness_score || 0), 0) / answers.length)
      : Math.round(latestEvaluation?.correctness_score ?? 0);

  const avgRelevance =
    answers.length > 0
      ? Math.round(answers.reduce((acc, a) => acc + (a.relevance_score || 0), 0) / answers.length)
      : Math.round(latestEvaluation?.relevance_score ?? 0);

  const avgCompleteness =
    answers.length > 0
      ? Math.round(answers.reduce((acc, a) => acc + (a.completeness_score || 0), 0) / answers.length)
      : Math.round(latestEvaluation?.completeness_score ?? 0);

  const avgClarity =
    answers.length > 0
      ? Math.round(answers.reduce((acc, a) => acc + (a.clarity_score || 0), 0) / answers.length)
      : Math.round(latestEvaluation?.clarity_score ?? 0);

  const avgTfidf =
    answers.length > 0
      ? Math.round(answers.reduce((acc, a) => acc + (a.tfidf_score || 0), 0) / answers.length)
      : Math.round(latestEvaluation?.tfidf_score ?? 0);

  const avgSemantic =
    answers.length > 0
      ? Math.round(answers.reduce((acc, a) => acc + (a.semantic_score || 0), 0) / answers.length)
      : Math.round(latestEvaluation?.semantic_score ?? 0);

  // Active question being reviewed
  const activeAnswer = answers[selectedQuestionIndex];

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.scrollContent}
      nestedScrollEnabled={true}
      showsVerticalScrollIndicator={true}
    >
      {/* Hero Score Badge */}
      <Card style={styles.scoreHeroCard}>
        <Text style={styles.heroTitle}>Interview Performance Evaluation</Text>
        <Text style={styles.heroSubtitle}>
          {sessionDetails
            ? `${sessionDetails.target_role} • ${sessionDetails.difficulty} • ${sessionDetails.interview_type}`
            : "Mock Interview Report"}
        </Text>
        <View
          style={[
            styles.scoreCircle,
            { borderColor: getScoreColor(effectiveScore) },
          ]}
        >
          <Text
            style={[
              styles.scoreNumber,
              { color: getScoreColor(effectiveScore) },
            ]}
          >
            {effectiveScore}%
          </Text>
          <Text style={styles.scoreSubtext}>Overall Score</Text>
        </View>
        <Text style={styles.heroSummary}>
          {effectiveScore >= 70
            ? "Strong performance! Your answers demonstrate solid technical competence and clear explanations."
            : effectiveScore >= 45
            ? "Good effort. Review the missing technical concepts below to raise your placement readiness."
            : "Foundational practice needed. Review the benchmark model answers to master core concepts."}
        </Text>
      </Card>

      {/* Aggregate Rubric Breakdown across all questions */}
      <Text style={styles.sectionTitle}>Overall Rubric Dimensions</Text>
      <Card style={styles.rubricCard}>
        <View style={styles.rubricRow}>
          <View style={styles.rubricItem}>
            <Text style={styles.rubricScore}>{avgCorrectness}%</Text>
            <Text style={styles.rubricLabel}>Technical Correctness</Text>
          </View>
          <View style={styles.rubricDivider} />
          <View style={styles.rubricItem}>
            <Text style={styles.rubricScore}>{avgRelevance}%</Text>
            <Text style={styles.rubricLabel}>Relevance & Focus</Text>
          </View>
        </View>

        <View style={styles.horizontalDivider} />

        <View style={styles.rubricRow}>
          <View style={styles.rubricItem}>
            <Text style={styles.rubricScore}>{avgCompleteness}%</Text>
            <Text style={styles.rubricLabel}>Depth & Completeness</Text>
          </View>
          <View style={styles.rubricDivider} />
          <View style={styles.rubricItem}>
            <Text style={styles.rubricScore}>{avgClarity}%</Text>
            <Text style={styles.rubricLabel}>Structure & Clarity</Text>
          </View>
        </View>
      </Card>

      {/* Lexical vs Semantic Understanding */}
      <Card style={styles.comparisonCard}>
        <Text style={styles.cardHeader}>ML & AI Analysis Breakdown</Text>
        <View style={styles.compRow}>
          <Text style={styles.compLabel}>TF-IDF Lexical Similarity:</Text>
          <Text style={styles.compValue}>{avgTfidf}%</Text>
        </View>
        <View style={styles.compRow}>
          <Text style={styles.compLabel}>Semantic Concept Alignment:</Text>
          <Text style={styles.compValue}>{avgSemantic}%</Text>
        </View>
      </Card>

      {/* Question-by-Question Deep Dive */}
      <Text style={styles.sectionTitle}>Question-by-Question Deep Dive</Text>

      {loadingDetails ? (
        <Card style={styles.loadingCard}>
          <ActivityIndicator size="small" color={Colors.primary} />
          <Text style={styles.loadingText}>Loading full question-by-question breakdown...</Text>
        </Card>
      ) : answers.length > 0 ? (
        <>
          {/* Question Selector Tabs */}
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            style={styles.tabsScrollView}
            contentContainerStyle={styles.tabsContainer}
          >
            {answers.map((_, idx) => (
              <TouchableOpacity
                key={idx}
                style={[
                  styles.tabButton,
                  selectedQuestionIndex === idx && styles.tabButtonSelected,
                ]}
                onPress={() => setSelectedQuestionIndex(idx)}
              >
                <Text
                  style={[
                    styles.tabButtonText,
                    selectedQuestionIndex === idx && styles.tabButtonTextSelected,
                  ]}
                >
                  Question {idx + 1}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>

          {/* Detailed Question Review */}
          {activeAnswer && (
            <View style={styles.activeQuestionWrap}>
              {/* Question Text */}
              <Card style={styles.questionCard}>
                <View style={styles.questionHeaderRow}>
                  <Text style={styles.questionIndexBadge}>
                    Question {selectedQuestionIndex + 1} of {answers.length}
                  </Text>
                  {activeAnswer.response_time_seconds ? (
                    <Text style={styles.timeBadge}>
                      ⏱ {activeAnswer.response_time_seconds}s
                    </Text>
                  ) : null}
                </View>
                <Text style={styles.questionPrompt}>{activeAnswer.question_text}</Text>
              </Card>

              {/* Follow-up question banner if asked */}
              {activeAnswer.follow_up_question ? (
                <Card style={styles.reviewedFollowUpCard}>
                  <Text style={styles.reviewedFollowUpBadge}>💡 ADAPTIVE FOLLOW-UP ASKED</Text>
                  <Text style={styles.reviewedFollowUpText}>{activeAnswer.follow_up_question}</Text>
                </Card>
              ) : null}

              {/* Candidate's Answer */}
              <Card style={styles.userAnswerCard}>
                <Text style={styles.userAnswerHeading}>Your Response</Text>
                <Text style={styles.userAnswerContent}>{activeAnswer.candidate_answer}</Text>
              </Card>

              {/* Missing Concepts for this Question */}
              {activeAnswer.missing_concepts && activeAnswer.missing_concepts.length > 0 && (
                <Card style={styles.warningCard}>
                  <Text style={styles.warningTitle}>⚠️ Key Concepts Missed in this Answer</Text>
                  <View style={styles.conceptsWrap}>
                    {activeAnswer.missing_concepts.map((concept, idx) => (
                      <View key={idx} style={styles.conceptChip}>
                        <Text style={styles.conceptText}>{concept}</Text>
                      </View>
                    ))}
                  </View>
                </Card>
              )}

              {/* Strengths & Actionable Improvements */}
              <Card style={styles.feedbackCard}>
                <Text style={styles.feedbackHeading}>💪 What You Did Well</Text>
                <Text style={styles.feedbackText}>
                  {activeAnswer.feedback_strengths || "Attempted answer."}
                </Text>

                <View style={styles.feedbackDivider} />

                <Text style={styles.feedbackHeading}>🎯 Actionable Improvements</Text>
                <Text style={styles.feedbackText}>
                  {activeAnswer.feedback_improvements || "Cover essential definitions and give concrete examples."}
                </Text>
              </Card>

              {/* Benchmark Model Answer */}
              {activeAnswer.model_answer ? (
                <Card style={styles.modelAnswerCard}>
                  <Text style={styles.modelAnswerTitle}>📖 High-Scoring Benchmark Answer</Text>
                  <Text style={styles.modelAnswerText}>{activeAnswer.model_answer}</Text>
                </Card>
              ) : null}
            </View>
          )}
        </>
      ) : latestEvaluation ? (
        // Fallback to single latestEvaluation if session answers list was empty
        <>
          {latestEvaluation.missing_concepts.length > 0 && (
            <Card style={styles.warningCard}>
              <Text style={styles.warningTitle}>⚠️ Key Concepts Missed</Text>
              <View style={styles.conceptsWrap}>
                {latestEvaluation.missing_concepts.map((concept, idx) => (
                  <View key={idx} style={styles.conceptChip}>
                    <Text style={styles.conceptText}>{concept}</Text>
                  </View>
                ))}
              </View>
            </Card>
          )}
          <Card style={styles.feedbackCard}>
            <Text style={styles.feedbackHeading}>💪 What You Did Well</Text>
            <Text style={styles.feedbackText}>{latestEvaluation.feedback_strengths}</Text>
            <View style={styles.feedbackDivider} />
            <Text style={styles.feedbackHeading}>🎯 Actionable Improvements</Text>
            <Text style={styles.feedbackText}>{latestEvaluation.feedback_improvements}</Text>
          </Card>
          <Card style={styles.modelAnswerCard}>
            <Text style={styles.modelAnswerTitle}>📖 High-Scoring Benchmark Answer</Text>
            <Text style={styles.modelAnswerText}>{latestEvaluation.model_answer}</Text>
          </Card>
        </>
      ) : null}

      {/* Action Buttons */}
      {(() => {
        const allMissed = Array.from(
          new Set([
            ...answers.flatMap((a) => a.missing_concepts || []),
            ...(latestEvaluation?.missing_concepts || []),
          ])
        );

        if (allMissed.length > 0) {
          const sample = allMissed.slice(0, 3).join(", ");
          return (
            <Button
              title={`⚡ Practice Weak Topics (${sample})`}
              onPress={() =>
                navigation.navigate("SetupInterview", {
                  prefillTrack: (sessionDetails?.interview_type as any) || "Technical",
                  prefillRole: sessionDetails?.target_role,
                  prefillDifficulty: (sessionDetails?.difficulty as any) || "Fresher",
                  prefillTopics: allMissed.slice(0, 4).join(", "),
                })
              }
              style={styles.weakTopicsButton}
            />
          );
        }
        return null;
      })()}

      <Button
        title="⚡ Start New Practice Simulation"
        onPress={() => navigation.navigate("SetupInterview")}
        style={styles.actionButton}
      />
      <Button
        title="View All Past Interviews"
        variant="outline"
        onPress={() => navigation.navigate("History")}
        style={styles.actionButton}
      />
      <Button
        title="Return to Dashboard"
        variant="outline"
        onPress={() => navigation.navigate("Dashboard")}
        style={styles.actionButton}
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
  scoreHeroCard: {
    alignItems: "center",
    padding: 24,
    marginBottom: 20,
  },
  heroTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 4,
  },
  heroSubtitle: {
    fontSize: 13,
    color: Colors.textSecondary,
    marginBottom: 16,
  },
  scoreCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    borderWidth: 6,
    alignItems: "center",
    justifyContent: "center",
    marginVertical: 12,
  },
  scoreNumber: {
    fontSize: 32,
    fontWeight: "800",
  },
  scoreSubtext: {
    fontSize: 11,
    fontWeight: "600",
    color: Colors.textSecondary,
    marginTop: 2,
    textTransform: "uppercase",
  },
  heroSummary: {
    fontSize: 13,
    color: Colors.textSecondary,
    textAlign: "center",
    lineHeight: 18,
    marginTop: 8,
    paddingHorizontal: 8,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 10,
    marginTop: 10,
  },
  rubricCard: {
    padding: 16,
    marginBottom: 16,
  },
  rubricRow: {
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
  },
  rubricItem: {
    flex: 1,
    alignItems: "center",
  },
  rubricScore: {
    fontSize: 22,
    fontWeight: "800",
    color: Colors.primary,
  },
  rubricLabel: {
    fontSize: 12,
    fontWeight: "500",
    color: Colors.textSecondary,
    marginTop: 4,
    textAlign: "center",
  },
  rubricDivider: {
    width: 1,
    height: 40,
    backgroundColor: Colors.border,
  },
  horizontalDivider: {
    height: 1,
    backgroundColor: Colors.border,
    marginVertical: 12,
  },
  comparisonCard: {
    padding: 16,
    marginBottom: 16,
  },
  cardHeader: {
    fontSize: 14,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 10,
  },
  compRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 4,
  },
  compLabel: {
    fontSize: 13,
    color: Colors.textSecondary,
  },
  compValue: {
    fontSize: 14,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  loadingCard: {
    padding: 20,
    alignItems: "center",
    marginBottom: 16,
  },
  loadingText: {
    fontSize: 13,
    color: Colors.textSecondary,
    marginTop: 8,
  },
  tabsScrollView: {
    marginBottom: 12,
  },
  tabsContainer: {
    flexDirection: "row",
    gap: 8,
  },
  tabButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    backgroundColor: Colors.surface,
    borderWidth: 1.5,
    borderColor: Colors.border,
  },
  tabButtonSelected: {
    borderColor: Colors.primary,
    backgroundColor: Colors.primary,
  },
  tabButtonText: {
    fontSize: 13,
    fontWeight: "600",
    color: Colors.textSecondary,
  },
  tabButtonTextSelected: {
    color: Colors.textInverse,
  },
  activeQuestionWrap: {
    marginBottom: 16,
  },
  questionCard: {
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: Colors.primary,
  },
  questionHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  questionIndexBadge: {
    fontSize: 12,
    fontWeight: "700",
    color: Colors.primary,
    textTransform: "uppercase",
  },
  timeBadge: {
    fontSize: 12,
    fontWeight: "600",
    color: Colors.textSecondary,
  },
  questionPrompt: {
    fontSize: 15,
    fontWeight: "600",
    color: Colors.textPrimary,
    lineHeight: 22,
  },
  userAnswerCard: {
    padding: 16,
    marginBottom: 12,
  },
  userAnswerHeading: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.textSecondary,
    marginBottom: 8,
    textTransform: "uppercase",
  },
  userAnswerContent: {
    fontSize: 14,
    color: Colors.textPrimary,
    lineHeight: 20,
  },
  warningCard: {
    padding: 16,
    marginBottom: 12,
    backgroundColor: "#FFFBEB",
    borderColor: "#FCD34D",
  },
  warningTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: "#B45309",
    marginBottom: 8,
  },
  conceptsWrap: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
  },
  conceptChip: {
    backgroundColor: "#FEF3C7",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  conceptText: {
    fontSize: 12,
    color: "#92400E",
    fontWeight: "500",
  },
  feedbackCard: {
    padding: 16,
    marginBottom: 12,
  },
  feedbackHeading: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.textPrimary,
    marginBottom: 6,
  },
  feedbackText: {
    fontSize: 13,
    color: Colors.textSecondary,
    lineHeight: 19,
  },
  feedbackDivider: {
    height: 1,
    backgroundColor: Colors.border,
    marginVertical: 12,
  },
  modelAnswerCard: {
    padding: 16,
    marginBottom: 16,
    backgroundColor: "#F0FDF4",
    borderColor: "#86EFAC",
  },
  modelAnswerTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: "#166534",
    marginBottom: 8,
  },
  modelAnswerText: {
    fontSize: 13,
    color: "#14532D",
    lineHeight: 20,
  },
  reviewedFollowUpCard: {
    padding: 14,
    marginBottom: 12,
    backgroundColor: "#F0FDF4",
    borderLeftWidth: 4,
    borderLeftColor: Colors.success,
  },
  reviewedFollowUpBadge: {
    fontSize: 11,
    fontWeight: "800",
    color: "#166534",
    marginBottom: 4,
    letterSpacing: 0.5,
  },
  reviewedFollowUpText: {
    fontSize: 13,
    fontWeight: "600",
    color: "#14532D",
    lineHeight: 18,
  },
  actionButton: {
    marginBottom: 10,
  },
  weakTopicsButton: {
    marginBottom: 10,
    backgroundColor: Colors.accent,
  },
});
