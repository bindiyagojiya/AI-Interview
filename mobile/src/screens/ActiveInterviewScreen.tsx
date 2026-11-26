import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { RootStackParamList } from "../types/navigation";
import { apiClient } from "../services/api";
import { Question, SessionAnswerResponse, EvaluationResult } from "../types";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { ProgressBar } from "../components/ProgressBar";
import { Colors } from "../constants/colors";

type Props = NativeStackScreenProps<RootStackParamList, "ActiveInterview">;

export const ActiveInterviewScreen: React.FC<Props> = ({ route, navigation }) => {
  const { sessionId, interviewType, targetRole, difficulty, numQuestions = 5 } = route.params;

  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [questionNumber, setQuestionNumber] = useState(1);
  const [totalQuestions] = useState(numQuestions || 5);
  const [answerText, setAnswerText] = useState("");
  const [secondsRemaining, setSecondsRemaining] = useState(120); // 2 minutes per question
  const [loadingQuestion, setLoadingQuestion] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [evaluations, setEvaluations] = useState<EvaluationResult[]>([]);
  const [activeFollowUp, setActiveFollowUp] = useState<string | null>(null);
  const [initialAnswerSubmitted, setInitialAnswerSubmitted] = useState<string>("");

  // Fetch the next question
  const fetchNextQuestion = async (currentEvalCount = evaluations.length) => {
    try {
      setLoadingQuestion(true);
      setActiveFollowUp(null);
      setInitialAnswerSubmitted("");
      const response = await apiClient.get<Question | null>(
        `/interviews/${sessionId}/next-question`
      );

      if (response.data) {
        setCurrentQuestion(response.data);
        setAnswerText("");
        setSecondsRemaining(120);
      } else if (currentEvalCount > 0) {
        // Candidate has answered at least 1 question and no more remain -> Complete interview
        await completeInterview();
      } else {
        // First question returned null (empty question bank or track mismatch)
        Alert.alert(
          "Question Bank Notice",
          "No questions were found for this interview track yet. Returning to dashboard.",
          [
            {
              text: "OK",
              onPress: () => navigation.replace("Dashboard"),
            },
          ]
        );
      }
    } catch (err: any) {
      Alert.alert("Network Error", err.message || "Failed to load question from backend server.");
    } finally {
      setLoadingQuestion(false);
    }
  };

  useEffect(() => {
    fetchNextQuestion(0);
  }, []);

  // Timer countdown
  useEffect(() => {
    if (secondsRemaining <= 0 || submitting || loadingQuestion || !currentQuestion) return;

    const timer = setInterval(() => {
      setSecondsRemaining((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [secondsRemaining, submitting, loadingQuestion, currentQuestion]);

  const handleSubmitAnswer = async () => {
    if (!currentQuestion) return;

    if (!answerText.trim()) {
      Alert.alert("Empty Response", "Please type your answer before submitting.");
      return;
    }

    try {
      setSubmitting(true);
      const responseTime = 120 - secondsRemaining;

      if (activeFollowUp) {
        // Submitting follow-up clarification
        const response = await apiClient.post<SessionAnswerResponse>(
          `/interviews/${sessionId}/submit-answer`,
          {
            question_id: currentQuestion.id,
            candidate_answer: answerText.trim(),
            response_time_seconds: responseTime,
            is_follow_up: true,
            follow_up_question: activeFollowUp,
          }
        );

        const upgradedEval = response.data.evaluation;
        const updatedEvals =
          evaluations.length > 0
            ? [...evaluations.slice(0, -1), upgradedEval]
            : [upgradedEval];
        setEvaluations(updatedEvals);
        setActiveFollowUp(null);
        setInitialAnswerSubmitted("");
        setQuestionNumber((prev) => prev + 1);

        if (updatedEvals.length >= totalQuestions) {
          await completeInterview(updatedEvals);
        } else {
          await fetchNextQuestion(updatedEvals.length);
        }
      } else {
        // Submitting primary question answer
        const response = await apiClient.post<SessionAnswerResponse>(
          `/interviews/${sessionId}/submit-answer`,
          {
            question_id: currentQuestion.id,
            candidate_answer: answerText.trim(),
            response_time_seconds: responseTime,
            is_follow_up: false,
          }
        );

        const latestEval = response.data.evaluation;
        const updatedEvals = [...evaluations, latestEval];
        setEvaluations(updatedEvals);

        // Check if interviewer asks a contextual follow-up question
        if (response.data.follow_up?.needed && response.data.follow_up?.follow_up_question) {
          setInitialAnswerSubmitted(answerText.trim());
          setActiveFollowUp(response.data.follow_up.follow_up_question);
          setAnswerText("");
          setSecondsRemaining(90); // 90 seconds to elaborate
        } else {
          setQuestionNumber((prev) => prev + 1);
          if (updatedEvals.length >= totalQuestions) {
            await completeInterview(updatedEvals);
          } else {
            await fetchNextQuestion(updatedEvals.length);
          }
        }
      }
    } catch (err: any) {
      Alert.alert("Evaluation Error", err.message || "Failed to submit answer.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleSkipFollowUp = async () => {
    setActiveFollowUp(null);
    setInitialAnswerSubmitted("");
    setQuestionNumber((prev) => prev + 1);
    if (evaluations.length >= totalQuestions) {
      await completeInterview(evaluations);
    } else {
      await fetchNextQuestion(evaluations.length);
    }
  };

  const completeInterview = async (finalEvals = evaluations) => {
    try {
      const response = await apiClient.post(`/interviews/${sessionId}/finish`);
      const finalScore = response.data.overall_score || 0;

      navigation.replace("Results", {
        sessionId: sessionId,
        overallScore: finalScore,
        answersCount: finalEvals.length,
        latestEvaluation: finalEvals[finalEvals.length - 1],
      });
    } catch (err: any) {
      Alert.alert("Error", "Could not finalize session. Navigating to Dashboard.");
      navigation.navigate("Dashboard");
    }
  };

  const wordCount = answerText.trim().split(/\s+/).filter(Boolean).length;
  const minutes = Math.floor(secondsRemaining / 60);
  const seconds = secondsRemaining % 60;
  const timerDisplay = `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : undefined}
      style={styles.container}
    >
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        nestedScrollEnabled={true}
        showsVerticalScrollIndicator={true}
      >
        {/* Top Header & Timer */}
        <View style={styles.topBar}>
          <View style={styles.headerTitleWrap}>
            <Text style={styles.badge}>
              {interviewType} • {difficulty}
            </Text>
            <Text style={styles.roleTitle}>{targetRole}</Text>
          </View>
          <View
            style={[
              styles.timerBadge,
              secondsRemaining < 30 && styles.timerBadgeUrgent,
            ]}
          >
            <Text
              style={[
                styles.timerText,
                secondsRemaining < 30 && styles.timerTextUrgent,
              ]}
            >
              ⏱ {timerDisplay}
            </Text>
          </View>
        </View>

        {/* Progress Tracker */}
        <ProgressBar current={questionNumber} total={totalQuestions} />

        {/* Question Presentation Card */}
        <Card style={styles.questionCard}>
          <Text style={styles.questionIndex}>
            Question {questionNumber} of {totalQuestions}
          </Text>
          <Text style={styles.questionText}>
            {loadingQuestion
              ? "Fetching question from Interview Engine..."
              : currentQuestion?.question_text || "No question loaded."}
          </Text>
        </Card>

        {/* Follow-up question banner if active */}
        {activeFollowUp ? (
          <Card style={styles.followUpCard}>
            <View style={styles.followUpHeaderRow}>
              <Text style={styles.followUpBadge}>💡 INTERVIEWER PROBE & CLARIFICATION</Text>
              <Text style={styles.followUpType}>Adaptive Probe</Text>
            </View>
            <Text style={styles.followUpText}>{activeFollowUp}</Text>
            <Text style={styles.followUpHint}>
              The interviewer wants you to elaborate on this specific point before moving to the next topic.
            </Text>
            {initialAnswerSubmitted ? (
              <View style={styles.initialAnswerPreview}>
                <Text style={styles.initialAnswerLabel}>Your Initial Answer:</Text>
                <Text style={styles.initialAnswerText} numberOfLines={2}>
                  "{initialAnswerSubmitted}"
                </Text>
              </View>
            ) : null}
          </Card>
        ) : null}

        {/* Answer Input Card */}
        <Card style={styles.answerCard}>
          <View style={styles.answerHeaderRow}>
            <Text style={styles.answerLabel}>
              {activeFollowUp ? "Your Clarification / Elaboration" : "Your Response"}
            </Text>
            <Text style={styles.wordCount}>{wordCount} words</Text>
          </View>

          <TextInput
            style={styles.textInput}
            multiline
            scrollEnabled={false}
            placeholder={
              activeFollowUp
                ? "Elaborate on the interviewer's follow-up point with specifics or code..."
                : "Type your explanation here. Cover key definitions, technical mechanisms, and examples..."
            }
            placeholderTextColor={Colors.textMuted}
            value={answerText}
            onChangeText={setAnswerText}
            editable={!submitting && !loadingQuestion}
          />

          <Button
            title={
              submitting
                ? "Analyzing Answer with AI..."
                : activeFollowUp
                ? "Submit Clarification & Update Score →"
                : "Submit Answer & Continue →"
            }
            onPress={handleSubmitAnswer}
            loading={submitting}
            disabled={loadingQuestion || submitting || !currentQuestion}
            style={styles.submitButton}
          />

          {activeFollowUp ? (
            <Button
              title="Skip Follow-Up & Next Question →"
              variant="outline"
              onPress={handleSkipFollowUp}
              disabled={submitting}
              style={styles.skipButton}
            />
          ) : null}
        </Card>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    padding: 20,
    paddingBottom: 80,
  },
  topBar: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  headerTitleWrap: {
    flex: 1,
    marginRight: 10,
  },
  badge: {
    fontSize: 12,
    fontWeight: "700",
    color: Colors.primary,
    textTransform: "uppercase",
  },
  roleTitle: {
    fontSize: 16,
    fontWeight: "800",
    color: Colors.textPrimary,
    marginTop: 2,
  },
  timerBadge: {
    backgroundColor: Colors.surface,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  timerBadgeUrgent: {
    backgroundColor: "#FEE2E2",
    borderColor: Colors.danger,
  },
  timerText: {
    fontSize: 14,
    fontWeight: "700",
    color: Colors.textSecondary,
  },
  timerTextUrgent: {
    color: Colors.danger,
  },
  questionCard: {
    padding: 20,
    borderLeftWidth: 4,
    borderLeftColor: Colors.primary,
  },
  questionIndex: {
    fontSize: 13,
    fontWeight: "700",
    color: Colors.primary,
    textTransform: "uppercase",
    marginBottom: 8,
  },
  questionText: {
    fontSize: 17,
    fontWeight: "600",
    color: Colors.textPrimary,
    lineHeight: 24,
  },
  answerCard: {
    padding: 18,
    marginTop: 12,
  },
  answerHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  answerLabel: {
    fontSize: 14,
    fontWeight: "700",
    color: Colors.textPrimary,
  },
  wordCount: {
    fontSize: 12,
    fontWeight: "600",
    color: Colors.textMuted,
  },
  textInput: {
    backgroundColor: Colors.surface,
    borderRadius: 12,
    padding: 16,
    fontSize: 15,
    color: Colors.textPrimary,
    minHeight: 160,
    textAlignVertical: "top",
    lineHeight: 22,
  },
  submitButton: {
    marginTop: 16,
  },
  skipButton: {
    marginTop: 10,
    borderColor: Colors.border,
  },
  followUpCard: {
    padding: 18,
    marginTop: 12,
    backgroundColor: "#F0FDF4",
    borderWidth: 1.5,
    borderColor: "#86EFAC",
  },
  followUpHeaderRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  followUpBadge: {
    fontSize: 11,
    fontWeight: "800",
    color: "#166534",
    letterSpacing: 0.5,
  },
  followUpType: {
    fontSize: 11,
    fontWeight: "700",
    color: "#15803D",
    backgroundColor: "#DCFCE7",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  followUpText: {
    fontSize: 15,
    fontWeight: "700",
    color: "#14532D",
    lineHeight: 22,
    marginBottom: 6,
  },
  followUpHint: {
    fontSize: 12,
    color: "#166534",
    lineHeight: 16,
    fontStyle: "italic",
  },
  initialAnswerPreview: {
    marginTop: 10,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: "rgba(22, 101, 52, 0.2)",
  },
  initialAnswerLabel: {
    fontSize: 11,
    fontWeight: "700",
    color: "#15803D",
    textTransform: "uppercase",
  },
  initialAnswerText: {
    fontSize: 12,
    color: "#14532D",
    marginTop: 2,
    fontStyle: "italic",
  },
});
