from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.schemas.evaluation import EvaluationResult

# Question Schemas
class QuestionResponse(BaseModel):
    id: int
    category: str
    domain: str
    difficulty: str
    question_text: str
    model_config = ConfigDict(from_attributes=True)

# Interview Creation
class InterviewCreate(BaseModel):
    interview_type: str = Field(default="Technical", description="'Technical', 'HR', 'Behavioral', 'Coding', 'Project-Based'")
    target_role: str = Field(default="Software Engineer")
    difficulty: str = Field(default="Fresher", description="'Fresher', 'Intermediate', 'Advanced'")
    num_questions: int = Field(default=5, ge=1, le=20)
    topics: Optional[str] = Field(default=None, description="Optional specific technical topics (e.g. React Hooks, Docker, Joins)")

# Answer Submission
class AnswerSubmit(BaseModel):
    question_id: int
    candidate_answer: str = Field(..., min_length=1)
    response_time_seconds: Optional[int] = 0
    is_follow_up: Optional[bool] = False
    follow_up_question: Optional[str] = None

# Context-Aware Follow-Up Question
class FollowUpInfo(BaseModel):
    needed: bool = False
    follow_up_question: Optional[str] = None
    follow_up_type: Optional[str] = None  # "clarification", "example", "deep_dive"

# Answer Response
class AnswerResponse(BaseModel):
    id: int
    question_id: int
    candidate_answer: str
    evaluation: EvaluationResult
    follow_up: Optional[FollowUpInfo] = None
    model_config = ConfigDict(from_attributes=True)

# Interview Session Response
class InterviewSessionResponse(BaseModel):
    id: int
    interview_type: str
    target_role: str
    difficulty: str
    num_questions: Optional[int] = 5
    status: str
    overall_score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# Question-by-Question Detailed Answer Item
class AnswerDetailResponse(BaseModel):
    id: int
    question_id: int
    question_text: str
    candidate_answer: str
    response_time_seconds: Optional[int] = 0
    tfidf_score: float = 0.0
    semantic_score: float = 0.0
    correctness_score: float = 0.0
    relevance_score: float = 0.0
    completeness_score: float = 0.0
    clarity_score: float = 0.0
    missing_concepts: List[str] = []
    feedback_strengths: str = ""
    feedback_improvements: str = ""
    model_answer: str = ""
    follow_up_question: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# Full Session Details with All Question Evaluations
class InterviewSessionDetailResponse(BaseModel):
    id: int
    interview_type: str
    target_role: str
    difficulty: str
    num_questions: Optional[int] = 5
    status: str
    overall_score: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    answers: List[AnswerDetailResponse] = []
    model_config = ConfigDict(from_attributes=True)

# Personalized Practice Recommendations Schema
class PracticeRecommendationsResponse(BaseModel):
    total_sessions_analyzed: int
    overall_average_score: float
    weak_topics: List[str] = []
    lowest_scoring_track: str = "Technical"
    recommended_role: str = "Software Engineer"
    recommended_difficulty: str = "Fresher"
    actionable_advice: str
    model_config = ConfigDict(from_attributes=True)
