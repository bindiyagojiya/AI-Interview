import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User
from app.models.question import Question
from app.models.session import InterviewSession
from app.schemas.interview import InterviewCreate
from app.services.question_generator import prepare_session_questions, normalize_domain
from app.api.v1.endpoints.interviews import start_interview, get_next_question

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_normalize_domain():
    assert normalize_domain("Senior React Developer", "Technical") == "React"
    assert normalize_domain("Python Backend Engineer", "Technical") == "Python"
    assert normalize_domain("Java Spring Developer", "Technical") == "Java"
    assert normalize_domain("Data Scientist / ML", "Technical") == "Data Science"
    assert normalize_domain("DevOps Specialist", "Technical") == "DevOps"
    assert normalize_domain("HR Recruiter", "HR") == "Behavioral"
    assert normalize_domain("Cybersecurity Analyst", "Technical") == "Cybersecurity Analyst"

def test_fresher_python_questions(db_session):
    questions = prepare_session_questions(
        db=db_session,
        interview_type="Technical",
        target_role="Python Developer",
        difficulty="Fresher",
        count=3
    )
    assert len(questions) == 3
    for q in questions:
        assert q.domain == "Python"
        assert q.difficulty == "Fresher"
        assert len(q.key_concepts) > 0
        assert len(q.reference_answer) > 20

def test_advanced_react_questions(db_session):
    questions = prepare_session_questions(
        db=db_session,
        interview_type="Technical",
        target_role="React Frontend Architect",
        difficulty="Advanced",
        count=2
    )
    assert len(questions) == 2
    for q in questions:
        assert q.domain == "React"
        assert q.difficulty == "Advanced"
        # React advanced questions should cover fiber, code splitting, concurrent mode, etc.
        assert any(k in q.question_text.lower() for k in ["fiber", "splitting", "dom", "rendering"])

def test_custom_niche_role_synthesizer(db_session):
    questions = prepare_session_questions(
        db=db_session,
        interview_type="Technical",
        target_role="Blockchain Engineer",
        difficulty="Intermediate",
        count=3
    )
    assert len(questions) == 3
    for q in questions:
        assert q.domain == "Blockchain Engineer"
        assert q.difficulty == "Intermediate"
        assert "Blockchain Engineer" in q.question_text

def test_session_receives_assigned_question_sequence(db_session):
    user = User(email="role_tester@test.com", full_name="Role Tester", hashed_password="pwd")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    config = InterviewCreate(
        interview_type="Technical",
        target_role="Java Developer",
        difficulty="Intermediate",
        num_questions=3
    )
    session = start_interview(config=config, current_user=user, db=db_session)
    assert len(session.question_ids) == 3

    # Check that questions retrieved match Java Intermediate
    q1 = get_next_question(session_id=session.id, current_user=user, db=db_session)
    assert q1 is not None
    assert q1.domain == "Java"
    assert q1.difficulty == "Intermediate"
    assert q1.id == session.question_ids[0]

