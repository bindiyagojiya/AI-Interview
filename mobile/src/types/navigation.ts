import { EvaluationResult, InterviewSession } from "./index";

export type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  Dashboard: undefined;
  SetupInterview:
    | {
        prefillTrack?: "Technical" | "HR" | "Coding" | "Project-Based";
        prefillRole?: string;
        prefillTopics?: string;
        prefillDifficulty?: "Fresher" | "Intermediate" | "Advanced";
      }
    | undefined;
  ActiveInterview: {
    sessionId: number;
    interviewType: string;
    targetRole: string;
    difficulty: string;
    numQuestions: number;
  };
  Results: {
    sessionId: number;
    overallScore: number;
    answersCount: number;
    latestEvaluation?: EvaluationResult;
  };
  History: undefined;
  Analytics: undefined;
  Profile: undefined;
};
