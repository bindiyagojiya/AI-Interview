# System Architecture — InterviewIQ AI

## 1. High-Level Architecture Overview

InterviewIQ AI follows a decoupled 3-tier client-server architecture designed for high scalability, separation of concerns, and cross-platform readiness.

```
+-------------------------------------------------------------+
|                 PRESENTATION TIER (Mobile App)              |
|                   React Native + Expo (TS)                  |
|  - Auth Screens (Login / Register / Profile)                |
|  - Student Dashboard (Analytics / Quick Action Cards)       |
|  - Mock Interview Room (Sequential Q&A, Response Timer)     |
|  - Performance Breakdown & Detailed Feedback Screen         |
|  - Historical Session Review & Progress Tracking Screen     |
+------------------------------+------------------------------+
                               | HTTPS / REST (JSON)
                               | Authorization: Bearer <JWT>
+------------------------------v------------------------------+
|                    APPLICATION TIER (FastAPI)               |
|            Python 3.10+ Asynchronous Web Framework          |
|  +---------------------+  +-------------------------------+ |
|  | Auth Service        |  | Interview Session Manager     | |
|  | (Argon2 / JWT)      |  | (State & Question Sequencing) | |
|  +---------------------+  +-------------------------------+ |
|  +---------------------+  +-------------------------------+ |
|  | User & Profile Svc  |  | History & Analytics Service   | |
|  +---------------------+  +-------------------------------+ |
|  +--------------------------------------------------------+ |
|  | Hybrid ML & AI Evaluation Service                      | |
|  |  1. Baseline NLP: scikit-learn (TF-IDF & Cosine Sim)   | |
|  |  2. Semantic Evaluator: Rubric Scoring (4 Criteria)   | |
|  +--------------------------------------------------------+ |
+------------------+-----------------------+------------------+
                   |                       |
                   | SQLAlchemy 2.0 ORM    | Reference Concept Bank
                   v                       v
+------------------+---------+   +---------+------------------+
|           DATA TIER        |   |       BENCHMARKS & AI      |
|          PostgreSQL        |   |  - Curated Answer Corpus   |
|  - Users & Profiles        |   |  - Keyword Taxonomy        |
|  - Question Catalog        |   |  - LLM Provider / Fallback |
|  - Sessions & Transcripts  |   +----------------------------+
|  - Evaluation Scores       |
+----------------------------+
```

---

## 2. Technology Stack & Component Responsibilities

| Layer | Technology | Key Libraries | Responsibility |
|---|---|---|---|
| **Mobile Client** | React Native (Expo) | TypeScript, Expo Router / React Navigation, Axios, `expo-secure-store`, React Native Paper / Tailwind (NativeWind) | Android native mobile UI, token persistence, user interactions, audio capture (Phase 8). |
| **API Server** | FastAPI (Python) | Pydantic v2, Uvicorn, Python-Jose (JWT), Passlib / Argon2-cffi | REST endpoints, authentication gatekeeper, request validation, business logic orchestration. |
| **Data Layer** | PostgreSQL | SQLAlchemy 2.0 (ORM), Alembic (Migrations), Psycopg2 / Asyncpg | Relational storage for users, profiles, interview questions, session states, and evaluation records. |
| **ML & NLP Engine** | Python ML Ecosystem | scikit-learn, NumPy, Pandas, NLTK / Regex | Baseline lexical similarity calculation (TF-IDF, Cosine Similarity), keyword extraction, tokenization. |
| **AI Evaluation** | Semantic Evaluator | Google Gemini API (or local mock fallback) | Contextual rubric analysis across 4 dimensions: Technical Correctness, Relevance, Completeness, Clarity. |

---

## 3. Database Schema Design (Entity-Relationship)

```
[ users ]
  ├── id (UUID / Int, PK)
  ├── email (VARCHAR, Unique, Indexed)
  ├── hashed_password (VARCHAR)
  ├── full_name (VARCHAR)
  ├── created_at (TIMESTAMP)
  └── updated_at (TIMESTAMP)
        │
        │ 1:1
        ▼
[ profiles ]
  ├── id (UUID / Int, PK)
  ├── user_id (FK -> users.id)
  ├── education (VARCHAR)
  ├── target_role (VARCHAR)
  ├── skills (ARRAY / JSON)
  └── experience_level (VARCHAR: Fresher, Mid, Senior)

[ questions ]
  ├── id (UUID / Int, PK)
  ├── category (VARCHAR: Technical, HR)
  ├── domain (VARCHAR: Python, Java, SQL, DSA, Behavioral)
  ├── difficulty (VARCHAR: Easy, Medium, Hard)
  ├── question_text (TEXT)
  ├── reference_answer (TEXT)
  └── key_concepts (ARRAY / JSON)

[ interview_sessions ]
  ├── id (UUID / Int, PK)
  ├── user_id (FK -> users.id)
  ├── interview_type (VARCHAR: Technical, HR)
  ├── target_role (VARCHAR)
  ├── difficulty (VARCHAR)
  ├── status (VARCHAR: IN_PROGRESS, COMPLETED, ABANDONED)
  ├── overall_score (FLOAT)
  ├── created_at (TIMESTAMP)
  └── completed_at (TIMESTAMP)
        │
        │ 1:N
        ▼
[ session_answers ]
  ├── id (UUID / Int, PK)
  ├── session_id (FK -> interview_sessions.id)
  ├── question_id (FK -> questions.id)
  ├── candidate_answer (TEXT)
  ├── response_time_seconds (INT)
  ├── tfidf_similarity_score (FLOAT: 0-100)
  ├── semantic_score (FLOAT: 0-100)
  ├── correctness_score (FLOAT: 0-100)
  ├── relevance_score (FLOAT: 0-100)
  ├── completeness_score (FLOAT: 0-100)
  ├── clarity_score (FLOAT: 0-100)
  ├── missing_concepts (JSON)
  ├── feedback_strengths (TEXT)
  ├── feedback_improvements (TEXT)
  └── model_answer (TEXT)
```

---

## 4. API Endpoints Contract (High-Level)

### Authentication & Profiles
- `POST /api/v1/auth/register` — Register a new student account.
- `POST /api/v1/auth/login` — Authenticate and receive a JWT Bearer token.
- `GET  /api/v1/auth/me` — Retrieve authenticated user profile.
- `PUT  /api/v1/profile` — Update education, skills, and target job role.

### Interview Management
- `POST /api/v1/interviews/start` — Initialize a new interview session with parameters.
- `GET  /api/v1/interviews/{id}/next-question` — Retrieve the current or next question.
- `POST /api/v1/interviews/{id}/submit-answer` — Submit answer text, trigger ML pipeline, save scores.
- `POST /api/v1/interviews/{id}/finish` — Finalize session and aggregate total metrics.
- `GET  /api/v1/interviews/{id}/results` — Detailed feedback report and score breakdown.
- `GET  /api/v1/interviews/history` — List past interview sessions with high-level scores.

---

## 5. Security & Environment Configuration
- **Password Security**: Strong hashing using Argon2 or bcrypt with auto-salting.
- **Token Security**: Short-lived JWT access tokens; secret keys read from environment.
- **Android Dev Host Mapping**: Base URL automatically switches between `http://10.0.2.2:8000` (Android emulator) and machine LAN IP (physical phone).
- **Environment Separation**: `.env.example` provides template variables; actual `.env` is ignored by `.gitignore`.

