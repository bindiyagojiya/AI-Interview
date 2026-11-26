from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.user import User
from app.models.question import Question
from app.models.session import InterviewSession
from app.models.answer import SessionAnswer
from app.schemas.interview import (
    InterviewCreate, InterviewSessionResponse, QuestionResponse,
    AnswerSubmit, AnswerResponse, InterviewSessionDetailResponse,
    AnswerDetailResponse, FollowUpInfo, PracticeRecommendationsResponse
)
from app.schemas.evaluation import EvaluationResult
from app.api.v1.endpoints.auth import get_current_user
from app.services.evaluation_service import evaluation_service
from app.services.question_generator import prepare_session_questions
from app.db.init_db import seed_default_questions

router = APIRouter()

@router.post("/start", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
def start_interview(
    config: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initializes a new mock interview session with role & difficulty-tailored questions."""
    seed_default_questions(db)

    target_count = config.num_questions or 5

    # Prepare custom tailored questions for candidate's role, difficulty, and count
    custom_questions = prepare_session_questions(
        db=db,
        interview_type=config.interview_type,
        target_role=config.target_role,
        difficulty=config.difficulty,
        count=target_count,
        topics=config.topics
    )
    assigned_q_ids = [q.id for q in custom_questions]

    session = InterviewSession(
        user_id=current_user.id,
        interview_type=config.interview_type,
        target_role=config.target_role,
        difficulty=config.difficulty,
        num_questions=target_count,
        question_ids=assigned_q_ids,
        status="IN_PROGRESS"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/{session_id}/next-question", response_model=Optional[QuestionResponse])
def get_next_question(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves the next unanswered question for this interview session."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    
    if session.status != "IN_PROGRESS":
        raise HTTPException(status_code=400, detail="This session is already completed.")

    # Guard: Auto-seed if database is empty
    if db.query(Question).count() == 0:
        seed_default_questions(db)

    # Find IDs of already answered questions in this session
    answered_ids = [
        ans.question_id for ans in db.query(SessionAnswer.question_id).filter(
            SessionAnswer.session_id == session_id
        ).all()
    ]

    target_count = session.num_questions or 5
    if len(answered_ids) >= target_count:
        return None

    # If session has no assigned question_ids, populate them now
    if not session.question_ids:
        custom_questions = prepare_session_questions(
            db=db,
            interview_type=session.interview_type,
            target_role=session.target_role,
            difficulty=session.difficulty,
            count=target_count
        )
        session.question_ids = [q.id for q in custom_questions]
        db.commit()
        db.refresh(session)

    # Return the next unanswered question in the assigned sequence
    if session.question_ids and isinstance(session.question_ids, list):
        for qid in session.question_ids:
            if qid not in answered_ids:
                q = db.query(Question).filter(Question.id == qid).first()
                if q:
                    return q
        return None

    # Legacy fallback
    query = db.query(Question)
    if answered_ids:
        query = query.filter(~Question.id.in_(answered_ids))
    return query.first()

@router.post("/{session_id}/submit-answer", response_model=AnswerResponse)
def submit_answer(
    session_id: int,
    answer_in: AnswerSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submits an answer, evaluates it with the ML engine, and saves feedback."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    
    if session.status != "IN_PROGRESS":
        raise HTTPException(status_code=400, detail="Cannot submit answer to a completed session.")

    question = db.query(Question).filter(Question.id == answer_in.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    # Check if answer for this question already exists in this session (idempotency / follow-up guard)
    existing_answer = db.query(SessionAnswer).filter(
        SessionAnswer.session_id == session.id,
        SessionAnswer.question_id == question.id
    ).first()

    follow_up_info = None

    if answer_in.is_follow_up and existing_answer:
        # Candidate is answering the follow-up clarification question
        combined_text = f"{existing_answer.candidate_answer}\n\n[Clarification]: {answer_in.candidate_answer.strip()}"
        eval_result = evaluation_service.evaluate(
            candidate_answer=combined_text,
            reference_answer=question.reference_answer,
            key_concepts=question.key_concepts or []
        )
        existing_answer.candidate_answer = combined_text
        existing_answer.response_time_seconds = (existing_answer.response_time_seconds or 0) + (answer_in.response_time_seconds or 0)
        existing_answer.tfidf_similarity_score = eval_result.tfidf_score
        existing_answer.semantic_score = eval_result.semantic_score
        existing_answer.correctness_score = eval_result.correctness_score
        existing_answer.relevance_score = eval_result.relevance_score
        existing_answer.completeness_score = eval_result.completeness_score
        existing_answer.clarity_score = eval_result.clarity_score
        existing_answer.missing_concepts = eval_result.missing_concepts
        existing_answer.feedback_strengths = eval_result.feedback_strengths
        existing_answer.feedback_improvements = eval_result.feedback_improvements
        existing_answer.model_answer = eval_result.model_answer
        answer_record = existing_answer
        follow_up_info = FollowUpInfo(needed=False)
    else:
        # Initial submission for this question
        eval_result = evaluation_service.evaluate(
            candidate_answer=answer_in.candidate_answer.strip(),
            reference_answer=question.reference_answer,
            key_concepts=question.key_concepts or []
        )

        # Check if follow-up question is warranted
        follow_up_data = evaluation_service.generate_follow_up(
            question_text=question.question_text,
            candidate_answer=answer_in.candidate_answer.strip(),
            missing_concepts=eval_result.missing_concepts,
            covered_concepts=[c for c in (question.key_concepts or []) if c not in eval_result.missing_concepts],
            target_role=session.target_role,
            difficulty=session.difficulty,
            interview_type=session.interview_type
        )

        follow_up_question_text = follow_up_data["follow_up_question"] if follow_up_data else None
        if follow_up_data:
            follow_up_info = FollowUpInfo(
                needed=True,
                follow_up_question=follow_up_data["follow_up_question"],
                follow_up_type=follow_up_data["follow_up_type"]
            )
        else:
            follow_up_info = FollowUpInfo(needed=False)

        if existing_answer:
            existing_answer.candidate_answer = answer_in.candidate_answer.strip()
            existing_answer.response_time_seconds = answer_in.response_time_seconds
            existing_answer.tfidf_similarity_score = eval_result.tfidf_score
            existing_answer.semantic_score = eval_result.semantic_score
            existing_answer.correctness_score = eval_result.correctness_score
            existing_answer.relevance_score = eval_result.relevance_score
            existing_answer.completeness_score = eval_result.completeness_score
            existing_answer.clarity_score = eval_result.clarity_score
            existing_answer.missing_concepts = eval_result.missing_concepts
            existing_answer.feedback_strengths = eval_result.feedback_strengths
            existing_answer.feedback_improvements = eval_result.feedback_improvements
            existing_answer.model_answer = eval_result.model_answer
            existing_answer.follow_up_question = follow_up_question_text
            answer_record = existing_answer
        else:
            answer_record = SessionAnswer(
                session_id=session.id,
                question_id=question.id,
                candidate_answer=answer_in.candidate_answer.strip(),
                response_time_seconds=answer_in.response_time_seconds,
                tfidf_similarity_score=eval_result.tfidf_score,
                semantic_score=eval_result.semantic_score,
                correctness_score=eval_result.correctness_score,
                relevance_score=eval_result.relevance_score,
                completeness_score=eval_result.completeness_score,
                clarity_score=eval_result.clarity_score,
                missing_concepts=eval_result.missing_concepts,
                feedback_strengths=eval_result.feedback_strengths,
                feedback_improvements=eval_result.feedback_improvements,
                model_answer=eval_result.model_answer,
                follow_up_question=follow_up_question_text
            )
            db.add(answer_record)

    db.commit()
    db.refresh(answer_record)

    return AnswerResponse(
        id=answer_record.id,
        question_id=answer_record.question_id,
        candidate_answer=answer_record.candidate_answer,
        evaluation=eval_result,
        follow_up=follow_up_info
    )

@router.get("/{session_id}/details", response_model=InterviewSessionDetailResponse)
def get_session_details(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns complete details of an interview session, including every question and evaluation."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    answers = db.query(SessionAnswer).filter(
        SessionAnswer.session_id == session.id
    ).order_by(SessionAnswer.id.asc()).all()

    answer_details = []
    for ans in answers:
        q_text = ans.question.question_text if ans.question else "Question text unavailable"
        answer_details.append(AnswerDetailResponse(
            id=ans.id,
            question_id=ans.question_id,
            question_text=q_text,
            candidate_answer=ans.candidate_answer,
            response_time_seconds=ans.response_time_seconds or 0,
            tfidf_score=ans.tfidf_similarity_score or 0.0,
            semantic_score=ans.semantic_score or 0.0,
            correctness_score=ans.correctness_score or 0.0,
            relevance_score=ans.relevance_score or 0.0,
            completeness_score=ans.completeness_score or 0.0,
            clarity_score=ans.clarity_score or 0.0,
            missing_concepts=ans.missing_concepts or [],
            feedback_strengths=ans.feedback_strengths or "",
            feedback_improvements=ans.feedback_improvements or "",
            model_answer=ans.model_answer or "",
            follow_up_question=ans.follow_up_question
        ))

    return InterviewSessionDetailResponse(
        id=session.id,
        interview_type=session.interview_type,
        target_role=session.target_role,
        difficulty=session.difficulty,
        num_questions=session.num_questions,
        status=session.status,
        overall_score=session.overall_score,
        created_at=session.created_at,
        completed_at=session.completed_at,
        answers=answer_details
    )

@router.post("/{session_id}/finish", response_model=InterviewSessionResponse)
def finish_interview(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marks interview as completed and calculates overall score."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    answers = db.query(SessionAnswer).filter(SessionAnswer.session_id == session_id).all()
    if answers:
        total = sum(
            ((a.tfidf_similarity_score or 0) * 0.25) + ((a.semantic_score or 0) * 0.75)
            for a in answers
        )
        session.overall_score = round(total / len(answers), 2)
    else:
        session.overall_score = 0.0

    session.status = "COMPLETED"
    session.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session

@router.get("/history", response_model=List[InterviewSessionResponse])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns past interview attempts for the current user."""
    return db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).order_by(InterviewSession.created_at.desc()).all()

@router.get("/recommendations", response_model=PracticeRecommendationsResponse)
def get_practice_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aggregates historical performance and concept gaps to generate personalized practice recommendations."""
    completed_sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.status == "COMPLETED"
    ).all()

    default_role = current_user.profile.target_role if current_user.profile and current_user.profile.target_role else "Software Engineer"
    default_diff = current_user.profile.experience_level if current_user.profile and current_user.profile.experience_level else "Fresher"

    if not completed_sessions:
        return PracticeRecommendationsResponse(
            total_sessions_analyzed=0,
            overall_average_score=0.0,
            weak_topics=[],
            lowest_scoring_track="Technical",
            recommended_role=default_role,
            recommended_difficulty=default_diff,
            actionable_advice="Take your first mock interview simulation to discover your key technical knowledge gaps and receive personalized practice focus."
        )

    # Calculate overall average
    scores = [s.overall_score for s in completed_sessions if s.overall_score is not None]
    overall_avg = round(sum(scores) / len(scores), 2) if scores else 0.0

    # Collect and rank frequently missed concepts
    session_ids = [s.id for s in completed_sessions]
    answers = db.query(SessionAnswer).filter(SessionAnswer.session_id.in_(session_ids)).all()

    concept_freq = {}
    for ans in answers:
        for concept in (ans.missing_concepts or []):
            clean_c = concept.strip()
            if clean_c:
                concept_freq[clean_c] = concept_freq.get(clean_c, 0) + 1

    sorted_weak_topics = sorted(concept_freq.keys(), key=lambda k: concept_freq[k], reverse=True)[:5]

    # Lowest scoring track
    track_scores = {}
    for s in completed_sessions:
        if s.overall_score is not None:
            track_scores.setdefault(s.interview_type, []).append(s.overall_score)

    if track_scores:
        lowest_track = min(track_scores.keys(), key=lambda t: sum(track_scores[t]) / len(track_scores[t]))
    else:
        lowest_track = completed_sessions[0].interview_type if completed_sessions else "Technical"

    # Dynamic difficulty recommendation
    if overall_avg >= 75:
        rec_diff = "Intermediate" if default_diff == "Fresher" else "Advanced"
    elif overall_avg >= 50:
        rec_diff = "Intermediate"
    else:
        rec_diff = "Fresher"

    # Actionable advice formulation
    if sorted_weak_topics:
        top_str = ", ".join(sorted_weak_topics[:3])
        advice = f"Focus your next session on {top_str}. Mastering these frequently missed concepts will boost your {lowest_track} placement readiness."
    else:
        advice = f"Consistent performance demonstrated across {len(completed_sessions)} sessions! Push to {rec_diff} difficulty to tackle system design and edge cases."

    return PracticeRecommendationsResponse(
        total_sessions_analyzed=len(completed_sessions),
        overall_average_score=overall_avg,
        weak_topics=sorted_weak_topics,
        lowest_scoring_track=lowest_track,
        recommended_role=completed_sessions[-1].target_role if completed_sessions else default_role,
        recommended_difficulty=rec_diff,
        actionable_advice=advice
    )
