from sqlalchemy import Column, Integer, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class SessionAnswer(Base):
    __tablename__ = "session_answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    candidate_answer = Column(Text, nullable=False)
    response_time_seconds = Column(Integer, nullable=True)

    # ML & Rubric Evaluation Scores (0-100)
    tfidf_similarity_score = Column(Float, nullable=True)
    semantic_score = Column(Float, nullable=True)
    correctness_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)

    # Detailed Feedback
    missing_concepts = Column(JSON, nullable=True, default=list)
    feedback_strengths = Column(Text, nullable=True)
    feedback_improvements = Column(Text, nullable=True)
    model_answer = Column(Text, nullable=True)
    follow_up_question = Column(Text, nullable=True)

    # Relationships
    session = relationship("InterviewSession", back_populates="answers")
    question = relationship("Question")

