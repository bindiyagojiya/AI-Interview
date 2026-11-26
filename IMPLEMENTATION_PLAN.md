# Implementation Plan — InterviewIQ AI

## Overview
This document outlines the step-by-step roadmap for developing InterviewIQ AI. Each phase is subdivided into discrete, verifiable tasks with strict acceptance criteria and testing requirements.

---

## Phase 0: Project Setup & Persistent Memory (Current Phase)
- **Task 0.1**: Initialize project documentation (`PROJECT_OVERVIEW.md`, `ARCHITECTURE.md`, `IMPLEMENTATION_PLAN.md`, `PROJECT_STATUS.md`, `DECISIONS.md`, `TESTING.md`).
- **Task 0.2**: Verify toolchain prerequisites (Python, Node.js, Git, Postgres).
- **Task 0.3**: Setup project root directory structure (`/backend`, `/mobile`).
- **Acceptance Criteria**: All 6 documentation files exist; toolchain sanity check passes.

---

## Phase 1: Backend Foundation & Database (FastAPI + PostgreSQL)
- **Task 1.1**: Setup Python virtual environment & backend dependency management (`requirements.txt` / `pyproject.toml`).
- **Task 1.2**: Initialize FastAPI app structure (`app/core`, `app/api`, `app/models`, `app/schemas`, `app/services`, `app/db`).
- **Task 1.3**: Configure PostgreSQL connection with SQLAlchemy 2.0 and Alembic.
- **Task 1.4**: Implement initial database models (`User`, `Profile`) and run Alembic baseline migration.
- **Task 1.5**: Implement health-check endpoint (`GET /api/v1/health`) and verify with Pytest.
- **Acceptance Criteria**: FastAPI server runs; database tables successfully create; automated health test passes.

---

## Phase 2: Authentication & User Profiles Module
- **Task 2.1**: Implement password hashing utilities (Argon2 / bcrypt) and JWT token manager.
- **Task 2.2**: Implement user registration (`POST /api/v1/auth/register`) with Pydantic validation.
- **Task 2.3**: Implement login & token issuance (`POST /api/v1/auth/login`).
- **Task 2.4**: Implement protected user profile endpoints (`GET /api/v1/auth/me`, `PUT /api/v1/profile`).
- **Task 2.5**: Write Pytest test suite covering registration, duplicate email rejection, login, and token auth.
- **Acceptance Criteria**: All auth tests pass; valid JWT provides access to protected routes.

---

## Phase 3: Machine Learning & Answer Evaluation Engine
- **Task 3.1**: Create curated reference question-answer dataset with key concepts.
- **Task 3.2**: Implement Baseline NLP evaluator using `scikit-learn` (TF-IDF vectorizer + Cosine Similarity).
- **Task 3.3**: Implement keyword & concept coverage extractor.
- **Task 3.4**: Implement Semantic AI Rubric Evaluator (4 criteria: Relevance, Correctness, Completeness, Clarity) with mock/offline fallback.
- **Task 3.5**: Write unit tests comparing various answer qualities (good, partial, irrelevant, empty) to verify scoring stability.
- **Acceptance Criteria**: Evaluation pipeline accurately scores candidate answers and highlights missing concepts; tests pass.

---

## Phase 4: Interview Engine Backend (Sessions & Scoring APIs)
- **Task 4.1**: Create database models for `Question`, `InterviewSession`, and `SessionAnswer`.
- **Task 4.2**: Seed initial question catalog (Technical: Python, Java, SQL, DSA; HR/Behavioral).
- **Task 4.3**: Implement `POST /api/v1/interviews/start` to configure and launch a session.
- **Task 4.4**: Implement `GET /api/v1/interviews/{id}/next-question` for sequential delivery.
- **Task 4.5**: Implement `POST /api/v1/interviews/{id}/submit-answer` wired to the ML evaluation service.
- **Task 4.6**: Implement `POST /api/v1/interviews/{id}/finish` and `GET /api/v1/interviews/{id}/results`.
- **Task 4.7**: Write end-to-end backend tests for a complete mock interview session.
- **Acceptance Criteria**: Full interview lifecycle can be executed and scored purely via API; tests pass.

---

## Phase 5: Mobile App Foundation & Authentication (React Native + Expo)
- **Task 5.1**: Initialize React Native Expo app with TypeScript template in `/mobile`.
- **Task 5.2**: Setup mobile architecture (screens, components, services, navigation, theme).
- **Task 5.3**: Build API client with Axios, base URL resolver (10.0.2.2 vs localhost), and token interceptors.
- **Task 5.4**: Implement `SecureStore` helper for JWT management.
- **Task 5.5**: Build Login, Register, and Profile Setup screens.
- **Task 5.6**: Verify login and registration end-to-end between Android emulator/device and FastAPI.
- **Acceptance Criteria**: User can register and log in on mobile; token persists across app reloads.

---

## Phase 6: Mobile Interview Experience & Real-Time Flow
- **Task 6.1**: Build Student Dashboard (readiness stats, recent interviews, quick start button).
- **Task 6.2**: Build Interview Configuration screen (role, difficulty, technical vs. HR, length).
- **Task 6.3**: Build Active Mock Interview screen (one question at a time, question index indicator, countdown timer, text answer input, submit button).
- **Task 6.4**: Implement question transition state and loading indicators during ML evaluation.
- **Acceptance Criteria**: Candidate can configure and complete a multi-question text interview on Android.

---

## Phase 7: Results, Feedback & History Module
- **Task 7.1**: Build Results & Feedback screen (overall score badge, radar/category scores, strengths, weaknesses, model answer comparison).
- **Task 7.2**: Build Interview History screen (chronological list of attempts, filtering by topic/score).
- **Task 7.3**: Build Detailed Past Interview Review modal.
- **Acceptance Criteria**: Completed interviews display comprehensive feedback and appear correctly in student history.

---

## Phase 8: Voice Interview Integration (STT / Audio Playback)
- **Task 8.1**: Integrate Expo Audio recording permissions and microphone UI controls.
- **Task 8.2**: Connect speech-to-text service for audio answer transcription.
- **Task 8.3**: Implement optional Text-to-Speech (TTS) for interviewer voice playback.
- **Task 8.4**: Add fallback to text mode on transcription errors or noisy environments.
- **Acceptance Criteria**: Candidate can speak their answer, see the transcribed text, and submit for evaluation.

---

## Phase 9: End-to-End Verification, Documentation & MCA Demo Prep
- **Task 9.1**: Complete system test run with fresh database.
- **Task 9.2**: Review project code against MCA evaluation guidelines and academic standards.
- **Task 9.3**: Prepare demonstration datasets, presentation walkthrough script, and deployment documentation.
- **Acceptance Criteria**: Full working system verified without errors; all documentation updated.

