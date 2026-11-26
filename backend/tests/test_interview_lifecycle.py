import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User
from app.models.question import Question
from app.models.session import InterviewSession
from app.models.answer import SessionAnswer
from app.schemas.interview import InterviewCreate, AnswerSubmit
from app.api.v1.endpoints.interviews import (
    start_interview, get_next_question, submit_answer, finish_interview, get_history,
    get_session_details, get_practice_recommendations
)
from app.api.v1.endpoints.questions import get_questions

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

def test_complete_interview_lifecycle(db_session):
    # 1. Create candidate user
    user = User(email="candidate@test.com", full_name="Candidate One", hashed_password="hashed_pwd")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 2. Seed question bank
    questions = get_questions(db=db_session)
    assert len(questions) >= 5

    # 3. Start a technical interview session
    config = InterviewCreate(
        interview_type="Technical",
        target_role="Python Developer",
        difficulty="Fresher",
        num_questions=3
    )
    session = start_interview(config=config, current_user=user, db=db_session)
    assert session.id is not None
    assert session.status == "IN_PROGRESS"
    assert session.overall_score is None

    # 4. Fetch the first question
    next_q = get_next_question(session_id=session.id, current_user=user, db=db_session)
    assert next_q is not None
    assert next_q.category == "Technical"

    # 5. Submit candidate's answer for question 1
    answer_payload = AnswerSubmit(
        question_id=next_q.id,
        candidate_answer="List comprehensions provide a concise syntax for creating lists from iterables with clean readability and performance.",
        response_time_seconds=45
    )
    answer_res = submit_answer(
        session_id=session.id,
        answer_in=answer_payload,
        current_user=user,
        db=db_session
    )
    assert answer_res.id is not None
    assert answer_res.evaluation.overall_score > 50.0
    assert answer_res.evaluation.tfidf_score > 25.0
    assert len(answer_res.evaluation.feedback_strengths) > 0

    # 6. Finalize interview session
    completed_session = finish_interview(session_id=session.id, current_user=user, db=db_session)
    assert completed_session.status == "COMPLETED"
    assert completed_session.overall_score > 50.0
    assert completed_session.completed_at is not None

    # 7. Check interview history
    history = get_history(current_user=user, db=db_session)
    assert len(history) == 1
    assert history[0].id == session.id
    assert history[0].overall_score == completed_session.overall_score

def test_num_questions_limit_enforced(db_session):
    user = User(email="limit_test@test.com", full_name="Limit Tester", hashed_password="hashed_pwd")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Seed questions
    get_questions(db=db_session)

    # Create interview with exactly 3 questions
    config = InterviewCreate(
        interview_type="Technical",
        target_role="Software Engineer",
        difficulty="Fresher",
        num_questions=3
    )
    session = start_interview(config=config, current_user=user, db=db_session)
    assert session.num_questions == 3

    # Answer 3 questions
    for i in range(3):
        q = get_next_question(session_id=session.id, current_user=user, db=db_session)
        assert q is not None, f"Expected question {i+1} to be available"
        submit_answer(
            session_id=session.id,
            answer_in=AnswerSubmit(
                question_id=q.id,
                candidate_answer=f"Sample answer response for question index {i}",
                response_time_seconds=30
            ),
            current_user=user,
            db=db_session
        )

    # 4th call to get_next_question should return None because 3 of 3 have been answered
    q4 = get_next_question(session_id=session.id, current_user=user, db=db_session)
    assert q4 is None, "Expected get_next_question to return None after reaching num_questions limit"

def test_get_session_details_and_idempotency(db_session):
    user = User(email="detail_tester@test.com", full_name="Detail Tester", hashed_password="pwd")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    config = InterviewCreate(
        interview_type="Technical",
        target_role="Python Developer",
        difficulty="Fresher",
        num_questions=2
    )
    session = start_interview(config=config, current_user=user, db=db_session)

    # 1. Answer question 1
    q1 = get_next_question(session_id=session.id, current_user=user, db=db_session)
    assert q1 is not None

    submit_answer(
        session_id=session.id,
        answer_in=AnswerSubmit(
            question_id=q1.id,
            candidate_answer="Initial answer regarding list comprehensions in Python.",
            response_time_seconds=25
        ),
        current_user=user,
        db=db_session
    )

    # 2. Re-submit answer for question 1 (idempotency check)
    updated_res = submit_answer(
        session_id=session.id,
        answer_in=AnswerSubmit(
            question_id=q1.id,
            candidate_answer="Updated improved answer: list comprehensions offer concise syntax and faster loop execution.",
            response_time_seconds=40
        ),
        current_user=user,
        db=db_session
    )
    assert "concise syntax" in updated_res.candidate_answer

    # Verify only 1 answer row exists in database for this question
    answers_count = db_session.query(SessionAnswer).filter(
        SessionAnswer.session_id == session.id,
        SessionAnswer.question_id == q1.id
    ).count()
    assert answers_count == 1, "Expected duplicate submission to update existing row rather than insert a new one"

    # Finish interview
    finish_interview(session_id=session.id, current_user=user, db=db_session)

    # 3. Retrieve detailed session report
    details = get_session_details(session_id=session.id, current_user=user, db=db_session)
    assert details.id == session.id
    assert len(details.answers) == 1
    assert details.answers[0].question_text == q1.question_text
    assert details.answers[0].candidate_answer == "Updated improved answer: list comprehensions offer concise syntax and faster loop execution."
    assert details.answers[0].correctness_score > 0
    assert len(details.answers[0].model_answer) > 0

def test_context_aware_follow_up_questioning(db_session):
    user = User(email="followup_tester@test.com", full_name="Followup Tester", hashed_password="pwd")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    config = InterviewCreate(
        interview_type="Technical",
        target_role="Python Developer",
        difficulty="Intermediate",
        num_questions=1
    )
    session = start_interview(config=config, current_user=user, db=db_session)
    q1 = get_next_question(session_id=session.id, current_user=user, db=db_session)
    assert q1 is not None

    # Step 1: Submit brief conceptual answer (triggers follow-up request)
    brief_answer = AnswerSubmit(
        question_id=q1.id,
        candidate_answer="A list is mutable while a tuple is immutable.",
        response_time_seconds=15,
        is_follow_up=False
    )
    res1 = submit_answer(session_id=session.id, answer_in=brief_answer, current_user=user, db=db_session)
    assert res1.follow_up is not None
    assert res1.follow_up.needed is True
    assert len(res1.follow_up.follow_up_question) > 10

    initial_score = res1.evaluation.overall_score

    # Step 2: Answer the follow-up clarification question
    follow_up_answer = AnswerSubmit(
        question_id=q1.id,
        candidate_answer="Tuples are preferable for fixed collections because their immutability guarantees data integrity, enables use as dictionary keys, and uses less memory overhead.",
        response_time_seconds=25,
        is_follow_up=True,
        follow_up_question=res1.follow_up.follow_up_question
    )
    res2 = submit_answer(session_id=session.id, answer_in=follow_up_answer, current_user=user, db=db_session)
    assert res2.follow_up is not None
    assert res2.follow_up.needed is False
    assert "[Clarification]:" in res2.candidate_answer
    assert res2.evaluation.overall_score > initial_score

def test_practice_recommendations_aggregation(db_session):
    user = User(email="rec_tester@test.com", full_name="Rec Tester", hashed_password="pwd")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 1. Empty state
    empty_recs = get_practice_recommendations(current_user=user, db=db_session)
    assert empty_recs.total_sessions_analyzed == 0
    assert len(empty_recs.weak_topics) == 0

    # 2. Complete an interview with missing concepts
    config = InterviewCreate(
        interview_type="Technical",
        target_role="Python Developer",
        difficulty="Fresher",
        num_questions=1
    )
    session = start_interview(config=config, current_user=user, db=db_session)
    q = get_next_question(session_id=session.id, current_user=user, db=db_session)

    # Submit an answer missing core concepts
    submit_answer(
        session_id=session.id,
        answer_in=AnswerSubmit(
            question_id=q.id,
            candidate_answer="This is a simple basic statement.",
            response_time_seconds=10
        ),
        current_user=user,
        db=db_session
    )
    finish_interview(session_id=session.id, current_user=user, db=db_session)

    # 3. Retrieve populated recommendations
    populated_recs = get_practice_recommendations(current_user=user, db=db_session)
    assert populated_recs.total_sessions_analyzed == 1
    assert len(populated_recs.weak_topics) > 0
    assert populated_recs.lowest_scoring_track == "Technical"
    assert len(populated_recs.actionable_advice) > 20





