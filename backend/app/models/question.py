from sqlalchemy import Column, Integer, String, Text, JSON
from app.db.base import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)  # "Technical", "HR"
    domain = Column(String(100), nullable=False)    # "Python", "Java", "SQL", "DSA", "Behavioral"
    difficulty = Column(String(50), nullable=False)  # "Fresher", "Intermediate", "Advanced"
    question_text = Column(Text, nullable=False)
    reference_answer = Column(Text, nullable=False)
    key_concepts = Column(JSON, nullable=False, default=list)  # Target keywords/phrases

