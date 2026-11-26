# Testing Strategy & Verification Log — InterviewIQ AI

## 1. Testing Strategy

InterviewIQ AI employs a multi-level testing strategy to ensure all software functions reliably before being considered "Done":

1. **Unit & Evaluation Tests (Backend)**:
   - Pytest for database models, auth hashing, JWT signing/verifying, and ML scoring stability.
   - Test ML evaluation against edge cases: empty strings, garbage text, completely correct answers, partially correct answers.
2. **Integration API Tests**:
   - Test endpoints using Pytest `TestClient` (FastAPI).
   - Verify complete interview session lifecycles (register -> login -> start interview -> submit answers -> finish session -> check results).
3. **Frontend & Mobile Verification**:
   - TypeScript compile-time type checks (`tsc --noEmit`).
   - Manual UI and flow verification on Android Emulator / physical device via Expo Go.

---

## 2. Test Execution Commands

### Backend Tests
```bash
# From backend directory
pytest -v
pytest tests/test_auth.py -v
pytest tests/test_evaluation.py -v
```

### Mobile Verification
```bash
# From mobile directory
npx tsc --noEmit
npx expo start
```

---

## 3. Test Verification Log

| Date | Phase / Task | Test Suite / Command | Result | Notes |
|---|---|---|---|---|
| 2026-10-24 | Phase 0 | Initial documentation check | PASS | All 6 persistent tracking documents created |
| 2026-10-24 | Phase 0 | Toolchain Environment Check | PARTIAL | Node 22.19.0, npm 10.9.3, Git 2.52.0, Postgres 18.1 verified. Python binary missing from Python313. |
| 2026-10-24 | Phase 0/1 | Backend Architecture Scaffolding | PASS | Models, schemas, hybrid ML evaluator, auth, and API routes created |
| 2026-10-24 | Phase 5/6 | Mobile App Architecture Scaffolding | PASS | Expo TS structure, 7 screens, navigation, API client, & design system created |
| 2026-10-24 | Phase 1-4 | Automated Pytest Suite Execution | PASS | 9/9 tests passed (Auth, ML Evaluation, Health, Interview Lifecycle) |
| 2026-10-26 | Phase 5 | Mobile Dependency Resolution | PASS | Installed `expo-asset`, `react-dom@18.3.1`, `react-native-web`; `tsc --noEmit` PASS (0 errors) |
| 2026-10-27 | Phase 6 | Android Emulator Scrolling Optimization | PASS | Replaced `behavior="height"`, enabled `nestedScrollEnabled`, added `flexGrow: 1` & `scrollEnabled={false}` on TextInput; `tsc --noEmit` PASS |
| 2026-10-27 | Phase 3-6 | Session Length Enforcement (3, 5, 10 Questions) | PASS | Stored `num_questions` in DB; enforced count in backend & mobile. 10/10 Pytest PASS (`test_num_questions_limit_enforced`), `tsc --noEmit` PASS (0 errors) |
| 2026-10-27 | Phase 3-6 | Role & Difficulty-Aware Question Generator | PASS | Created `question_generator.py` covering Fresher/Intermediate/Advanced for all roles. 15/15 Pytest PASS (`test_question_generator.py`), `tsc --noEmit` PASS (0 errors) |




