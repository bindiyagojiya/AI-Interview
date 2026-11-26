# Project Overview — InterviewIQ AI

## 1. Executive Summary
**InterviewIQ AI** is an intelligent mock interview platform designed for Android devices to help students and job seekers prepare for technical, HR, and campus placement interviews. Unlike superficial mock interview prototypes, InterviewIQ AI couples an interactive interview simulation engine with an objective, dual-layer Machine Learning evaluation pipeline: a fast, deterministic NLP baseline (TF-IDF and cosine similarity) alongside a semantic rubric evaluator (assessing technical correctness, relevance, completeness, and clarity).

---

## 2. Target Users & Problem Statement
### Target Users
- **MCA and Engineering Students**: Preparing for campus placements and technical rounds.
- **Entry-Level Job Seekers & Career Switchers**: Needing realistic interview practice, question exposure, and actionable feedback on communication and technical depth.

### Core Problems Addressed
1. **Lack of Objective Feedback**: Traditional peer interviews lack standardized evaluation criteria.
2. **Subjectivity in Self-Preparation**: Candidates cannot easily gauge if their answers cover key concepts.
3. **Interview Anxiety**: Lack of real-time timed simulation under pressure.
4. **No Measurable Progress**: Candidates rarely track improvement across technical categories over time.

---

## 3. Scope and Core Features

### MVP (Minimum Viable Product)
- **Module 1: Authentication & User Profile**: Secure registration, login, JWT token management, and profile customization (education, target role, technical skills, experience level).
- **Module 2: Student Dashboard**: Overall interview readiness score, recent attempt summaries, quick-start action cards, and progress metrics.
- **Module 3: Interview Configuration**: Customized sessions by type (Technical vs. HR), domain (Python, Java, DSA, Web Dev, SQL, etc.), difficulty (Fresher, Intermediate, Advanced), and duration.
- **Module 4: AI Interview Engine**: One-question-at-a-time sequence, response timer, text-based answer capture, session state tracking, and adaptive follow-up triggering.
- **Module 5: Machine Learning & Answer Evaluation**:
  - *Baseline NLP*: scikit-learn TF-IDF vectorization and cosine similarity against reference benchmark answers.
  - *Semantic Rubric AI*: 4-criteria evaluation (Relevance, Correctness, Completeness, Clarity) providing 0–100 score, missing technical concepts, and strengths/weaknesses.
- **Module 6: Results & Detailed Feedback**: Comprehensive score reports, radar metrics, identified gaps, and side-by-side comparison with a high-scoring model answer.
- **Module 7: Interview History & Analytics**: Persistent history of completed sessions, question-by-question review, and performance analytics over time.

### Post-MVP / Advanced Enhancements
- **Module 8: Voice Interviewing**: Speech-to-Text (STT) answer transcription and Text-to-Speech (TTS) audio question playback.
- **Resume & Job Description Tailoring**: Parsing uploaded resumes/JDs to curate hyper-targeted questions.
- **Cross-Platform Expansion**: Future web portal sharing the same FastAPI backend.

---

## 4. Key Constraints & Guiding Principles
1. **Strictly Working Software**: Every phase must be verified with automated or manual tests before progression.
2. **Deterministic Baseline + AI Rigour**: Similarity scores must not be treated as absolute proof of correctness; ML limitations must be clearly documented.
3. **No Hardcoded Secrets**: All keys, JWT secrets, and DB URLs stored exclusively in `.env` files.
4. **Zero Forced Cost**: Architecture supports free-tier LLM integrations (e.g., Google Gemini API) and full offline mock fallbacks.
5. **Clean Separation of Concerns**: Strict boundary between presentation (React Native), API/business logic (FastAPI), data persistence (PostgreSQL), and ML evaluation services.
