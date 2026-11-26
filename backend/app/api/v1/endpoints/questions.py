from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models.question import Question
from app.schemas.interview import QuestionResponse
from app.db.seeds import DEFAULT_QUESTIONS

router = APIRouter()

@router.get("", response_model=List[QuestionResponse])
def get_questions(
    category: Optional[str] = None,
    domain: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve questions filtered by category, domain, or difficulty."""
    query = db.query(Question)
    if category and isinstance(category, str):
        query = query.filter(Question.category.ilike(category))
    if domain and isinstance(domain, str):
        query = query.filter(Question.domain.ilike(domain))
    if difficulty and isinstance(difficulty, str):
        query = query.filter(Question.difficulty.ilike(difficulty))
    
    questions = query.all()
    # Auto-seed if database is empty
    if not questions and db.query(Question).count() == 0:
        for seed in DEFAULT_QUESTIONS:
            q = Question(**seed)
            db.add(q)
        db.commit()
        questions = query.all()

    return questions
