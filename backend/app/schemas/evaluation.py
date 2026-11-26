from pydantic import BaseModel, Field
from typing import List, Optional

class EvaluationResult(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    tfidf_score: float = Field(..., ge=0, le=100)
    semantic_score: float = Field(..., ge=0, le=100)
    
    # Rubric Dimensions (0-100)
    correctness_score: float = Field(..., ge=0, le=100)
    relevance_score: float = Field(..., ge=0, le=100)
    completeness_score: float = Field(..., ge=0, le=100)
    clarity_score: float = Field(..., ge=0, le=100)

    # Detailed Insights
    missing_concepts: List[str] = []
    feedback_strengths: str
    feedback_improvements: str
    model_answer: str

