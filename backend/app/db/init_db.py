from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.question import Question
from app.db.seeds import DEFAULT_QUESTIONS
import app.models  # Ensure all models are registered

def seed_default_questions(db):
    """Seeds the question bank if empty."""
    if db.query(Question).count() == 0:
        for seed in DEFAULT_QUESTIONS:
            q = Question(**seed)
            db.add(q)
        db.commit()
        print(f"Seeded {len(DEFAULT_QUESTIONS)} default interview questions.")

def init_db():
    """Initializes database schema and populates seed questions."""
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        seed_default_questions(db)
        db.close()
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Notice: Database initialization deferred: {e}")

if __name__ == "__main__":
    init_db()
