from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    education = Column(String(255), nullable=True)
    target_role = Column(String(100), nullable=True, default="Software Engineer")
    experience_level = Column(String(50), nullable=True, default="Fresher")  # Fresher, Intermediate, Senior
    skills = Column(JSON, nullable=True, default=list)  # e.g., ["Python", "SQL", "FastAPI"]

    # Relationship
    user = relationship("User", back_populates="profile")

