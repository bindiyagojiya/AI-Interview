// User & Auth
export interface UserProfile {
  id: number;
  user_id: number;
  education?: string;
  target_role: string;
  experience_level: string;
  skills: string[];
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  profile?: UserProfile;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Question & Interview
export interface Question {
  id: number;
  category: "Technical" | "HR";
  domain: string;
  difficulty: "Fresher" | "Intermediate" | "Advanced";
  question_text: string;
}

export interface EvaluationResult {
  overall_score: number;
  tfidf_score: number;
  semantic_score: number;
  correctness_score: number;
  relevance_score: number;
  completeness_score: number;
  clarity_score: number;
  missing_concepts: string[];
  feedback_strengths: string;
  feedback_improvements: string;
  model_answer: string;
  follow_up_question?: string;
}

export interface FollowUpInfo {
  needed: boolean;
  follow_up_question?: string;
  follow_up_type?: string;
}

export interface SessionAnswerResponse {
  id: number;
  question_id: number;
  candidate_answer: string;
  evaluation: EvaluationResult;
  follow_up?: FollowUpInfo;
}

export interface InterviewSession {
  id: number;
  interview_type: "Technical" | "HR";
  target_role: string;
  difficulty: string;
  num_questions?: number;
  status: "IN_PROGRESS" | "COMPLETED" | "ABANDONED";
  overall_score?: number;
  created_at: string;
  completed_at?: string;
}

export interface AnswerDetail {
  id: number;
  question_id: number;
  question_text: string;
  candidate_answer: string;
  response_time_seconds?: number;
  tfidf_score: number;
  semantic_score: number;
  correctness_score: number;
  relevance_score: number;
  completeness_score: number;
  clarity_score: number;
  missing_concepts: string[];
  feedback_strengths: string;
  feedback_improvements: string;
  model_answer: string;
  follow_up_question?: string;
}

export interface InterviewSessionDetail extends InterviewSession {
  answers: AnswerDetail[];
}

export interface PracticeRecommendations {
  total_sessions_analyzed: number;
  overall_average_score: number;
  weak_topics: string[];
  lowest_scoring_track: string;
  recommended_role: string;
  recommended_difficulty: string;
  actionable_advice: string;
}
