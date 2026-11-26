# Architectural Decision Records (ADR) — InterviewIQ AI

## ADR-001: Three-Tier Client-Server Architecture
- **Status**: Accepted
- **Context**: The project requires a real working Android application with AI/ML evaluation. In the future, a web interface or recruiter dashboard may be added without rewriting business logic.
- **Decision**: Decouple the frontend (React Native + Expo) from the backend (FastAPI + PostgreSQL) via RESTful JSON APIs.
- **Consequences**: Enables clean separation of concerns, independent testing of the ML and database layers, and zero duplication of logic when adding future client platforms.

---

## ADR-002: Hybrid Machine Learning & AI Evaluation Pipeline
- **Status**: Accepted
- **Context**: Relying exclusively on LLMs can be costly, non-deterministic, and prone to hallucinations or rate limits. Relying purely on traditional NLP (TF-IDF/cosine similarity) fails to recognize semantic equivalents (e.g. synonyms, paraphrasing).
- **Decision**: Implement a two-tiered evaluation strategy:
  1. **Deterministic Baseline**: scikit-learn TF-IDF vectorization and cosine similarity against reference benchmark answers to provide an objective lexical metric and keyword overlap score.
  2. **Semantic Rubric Evaluation**: Structured AI prompt evaluating 4 discrete criteria: Technical Correctness, Relevance, Completeness, and Clarity (0–100 score + missing concepts).
- **Consequences**: Provides high academic value for an MCA evaluation by demonstrating both foundational NLP and modern AI techniques, while including a deterministic fallback if external AI APIs fail.

---

## ADR-003: FastAPI as Backend Framework
- **Status**: Accepted
- **Context**: Need a Python web framework that natively interoperates with scikit-learn and ML libraries, provides async performance, and automatically documents endpoints.
- **Alternatives Considered**: Flask, Django.
- **Reason for Selection**: FastAPI provides automatic OpenAPI/Swagger documentation, fast execution via Starlette/Pydantic, and native async support.

---

## ADR-004: PostgreSQL with SQLAlchemy 2.0 & Alembic
- **Status**: Accepted
- **Context**: Need robust relational storage for complex relationships (Users -> Profiles, Sessions -> Questions -> Answers -> Feedback).
- **Reason for Selection**: PostgreSQL is the industry-standard open-source relational database. SQLAlchemy 2.0 provides type-safe ORM queries, and Alembic ensures schema migrations are version-controlled and reproducible.

---

## ADR-005: Cost-Free Developer Strategy for AI Evaluation
- **Status**: Accepted
- **Context**: Academic MCA projects should not force students to pay for cloud API credits.
- **Decision**: Default to Google Gemini API (developer free tier) and provide a deterministic offline mock evaluation service for zero-cost operation.

