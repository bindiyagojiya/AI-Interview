from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    interview_type = Column(String(50), nullable=False)  # "Technical", "HR"
    target_role = Column(String(100), nullable=False)
    difficulty = Column(String(50), nullable=False)
    num_questions = Column(Integer, default=5, nullable=True)  # Configured question count (3, 5, 10)
    question_ids = Column(JSON, default=list, nullable=True)   # Sequence of question IDs assigned to this session
    status = Column(String(50), default="IN_PROGRESS", nullable=False)  # IN_PROGRESS, COMPLETED, ABANDONED
    overall_score = Column(Float, nullable=True)  # Aggregated 0-100 score
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="interviews")
    answers = relationship("SessionAnswer", back_populates="session", cascade="all, delete-orphan")
