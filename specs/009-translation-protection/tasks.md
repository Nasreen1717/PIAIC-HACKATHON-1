# Tasks: Translation Protection with Authentication

**Feature**: `009-translation-protection`
**Input**: Design documents from `/specs/009-translation-protection/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅
**Timeline**: ~30 minutes total (matches user estimate)

---

## Organization Strategy

Tasks organized by user story priority (P1, P2) to enable independent implementation and testing. Setup and foundational tasks block all stories. Within each story, tests (optional) precede implementation. Parallelization marked with [P].

**Format**: `- [ ] [TaskID] [P?] [Story?] Description with file path`

---

## Dependency Graph

```
Phase 1: Setup (T001-T003)
    ↓
Phase 2: Foundational Backend (T004-T007) ← BLOCKS ALL STORIES
    ↓
Phase 3: User Story 1 (T008-T015) [PARALLEL]
         └─ US1a: Logged-in user translates (P1)
         └─ US1b: Backend rejects unauthorized (P1)
         └─ US1c: Mobile responsive (P2)
    ↓
Phase 4: User Story 2 (T016-T019) [PARALLEL]
         └─ US2: Logged-out user sees prompt (P1)
    ↓
Phase 5: Integration & Polish (T020-T023)
```

**Parallel Opportunities**:
- T008-T009 can run in parallel (different files)
- T010-T011 can run in parallel (test files)
- T012-T015 can run in parallel (separate components)
- T016-T017 can run in parallel (separate components)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project structure and prepare for implementation

- [x] T001 Verify project structure matches plan: check `/mnt/d/code/Hackathon-1/Front-End-Book/src/components/TranslationButton/` and `/mnt/d/code/Hackathon-1/backend/app/api/v1/` exist
- [x] T002 Verify existing dependencies: confirm `python-jose`, `fastapi`, `React`, `Docusaurus` installed in both frontend and backend
- [x] T003 [P] Create git feature branch from current `008-navbar-auth`: `git checkout -b 009-translation-protection`

---

## Phase 2: Foundational Backend Setup (Blocking Prerequisites)

**Purpose**: Core backend infrastructure MUST be complete before any user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Verify `get_current_user()` dependency exists in `/mnt/d/code/Hackathon-1/backend/app/routes/auth.py` and extracts JWT from Authorization header
- [x] T005 [P] Create new file `/mnt/d/code/Hackathon-1/backend/app/api/v1/translate.py` with empty router (skeleton only)
- [x] T006 [P] Create new file `/mnt/d/code/Hackathon-1/backend/app/schemas/translate.py` with TranslateRequest and TranslateResponse Pydantic models (from data-model.md)
- [x] T007 Register translate router in `/mnt/d/code/Hackathon-1/backend/app/main.py`: add import and `app.include_router(translate.router)`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1a - Logged-in User Translates Article (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can successfully translate article content to Urdu via protected endpoint

**Independent Test**: Sign in to application, navigate to article page, click "Translate to Urdu" button, verify translation endpoint is called with Authorization header and returns translated content

### Implementation for User Story 1a

- [x] T008 [P] [US1a] Implement POST `/api/v1/translate` endpoint in `/mnt/d/code/Hackathon-1/backend/app/api/v1/translate.py` with `get_current_user` dependency (from quickstart.md backend setup section)
- [x] T009 [P] [US1a] Add input validation in endpoint: reject empty text, enforce max 50k chars limit in `/mnt/d/code/Hackathon-1/backend/app/api/v1/translate.py`
- [x] T010 [US1a] Verify `useTranslation` hook in `/mnt/d/code/Hackathon-1/Front-End-Book/src/components/TranslationButton/useTranslation.ts` sends Authorization header with bearer token (check for `Authorization: Bearer ${token}` in fetch call)
- [ ] T011 [US1a] Test authenticated translation flow manually: start backend, sign in via frontend, click translate button, verify POST `/api/v1/translate` succeeds with 200 response

**Acceptance**: ✅ Logged-in user can translate; endpoint returns 200 with translated text

---

## Phase 3: User Story 1b - Backend Rejects Unauthorized Requests (Priority: P1)

**Goal**: Backend API enforces authentication via JWT validation; rejects requests without valid token

**Independent Test**: Call `/api/v1/translate` endpoint without Authorization header, verify 401 response; call with invalid/expired token, verify 401 response with error detail; call with valid token, verify 200 response

### Implementation for User Story 1b

- [ ] T012 [P] [US1b] Test unauthorized request (no token): run `curl -X POST http://localhost:8000/api/v1/translate -H "Content-Type: application/json" -d '{"text": "test"}'` and verify response is 401 with `{"detail": "Not authenticated"}`
- [ ] T013 [P] [US1b] Test invalid token: run curl with invalid token header and verify 401 with `{"detail": "Invalid or expired token"}`
- [ ] T014 [US1b] Verify `get_current_user` dependency in endpoint properly handles missing Authorization header (should raise HTTPException 401) — inspect `/mnt/d/code/Hackathon-1/backend/app/routes/auth.py:42-48` to confirm logic
- [ ] T015 [US1b] Verify backend logs authentication attempts: add logging to `/mnt/d/code/Hackathon-1/backend/app/api/v1/translate.py` with user email and timestamp on successful translation

**Acceptance**: ✅ All unauthorized requests rejected with 401; valid requests proceed

---

## Phase 3: User Story 1c - Mobile Responsive Design (Priority: P2)

**Goal**: Translation UI (button and authentication prompt) renders correctly on mobile devices (320px+)

**Independent Test**: View article on mobile device (or browser dev tools mobile emulation), verify translation button/prompt displays with proper spacing; verify touch targets are tap-friendly (≥44px)

### Implementation for User Story 1c

- [ ] T016 [P] [US1c] Verify existing CSS in `/mnt/d/code/Hackathon-1/Front-End-Book/src/components/TranslationButton/TranslationButton.module.css` includes mobile media queries: check lines 181-213 for `@media (max-width: 768px)` and `@media (max-width: 480px)` rules
- [ ] T017 [P] [US1c] Verify ProtectedFeature component in `/mnt/d/code/Hackathon-1/Front-End-Book/src/components/Auth/ProtectedFeature.tsx` renders responsive layout (check className applications)
- [ ] T018 [US1c] Test responsive layout manually: open frontend in mobile emulation (Chrome DevTools), navigate to article, verify button/prompt displays correctly at 320px, 768px, and desktop widths
- [ ] T019 [US1c] Verify error messages display properly on mobile: error container should have word-wrap enabled and action buttons should stack or wrap (verify CSS `word-break: break-word` and `flex-wrap` settings)

**Acceptance**: ✅ UI responsive on all device sizes; touch targets adequate

---

## Phase 4: User Story 2 - Logged-out User Sees Sign-In Prompt (Priority: P1)

**Goal**: Unauthenticated users see clear authentication prompt instead of translation button; links to signin/signup provided

**Independent Test**: Clear browser auth state (localStorage.clear()), navigate to article page, verify translation area shows prompt; click "Sign In to Continue" link, verify navigation to /signin; sign in and return to article, verify button now displays

### Implementation for User Story 2

- [ ] T020 [P] [US2] Verify ProtectedFeature wrapper in `/mnt/d/code/Hackathon-1/Front-End-Book/src/components/TranslationButton/index.tsx` is applied with `featureName="Article translation"` (line 57)
- [ ] T021 [P] [US2] Verify ProtectedFeature component in `/mnt/d/code/Hackathon-1/Front-End-Book/src/components/Auth/ProtectedFeature.tsx` displays correct messaging: check that prompt says "Article translation requires authentication" (or similar), includes links to /signin and /signup
- [ ] T022 [US2] Test logged-out state manually: clear localStorage via `localStorage.clear()` in browser console, reload article page, verify prompt displays with "Sign in to translate" button
- [ ] T023 [US2] Verify signin flow: click "Sign In to Continue", sign in with valid credentials, return to article, verify translation button now displays and is enabled

**Acceptance**: ✅ Logged-out users see authentication prompt; signin flow works; button reappears after authentication

---

## Phase 5: Integration & End-to-End Testing

**Purpose**: Verify all user stories work together; test edge cases and error scenarios

- [ ] T024 End-to-end test full user flow: logout → see prompt → signin → translate → logout → see prompt again in `/mnt/d/code/Hackathon-1/Front-End-Book` (manual browser test)
- [ ] T025 Test token expiration: manually invalidate token in localStorage (change first 10 chars), attempt translation, verify 401 error and auth state clears
- [ ] T026 [P] Test error handling: call endpoint with invalid JSON in request body, verify 400 response with clear error message
- [ ] T027 [P] Test CORS headers: verify Authorization header allowed in CORS middleware in `/mnt/d/code/Hackathon-1/backend/app/main.py` (check `allow_headers=["*"]`)
- [ ] T028 Verify logs: check backend logs for authentication events, translation requests, and errors

**Checkpoint**: All user stories work independently and together; no console errors

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Code quality, documentation, and final verification

- [ ] T029 Code review: self-review changes against quickstart.md checklist (all files created/modified as documented)
- [ ] T030 Update frontend: verify useTranslation hook properly handles 401 response (clear auth state and show login prompt) in `/mnt/d/code/Hackathon-1/Front-End-Book/src/components/TranslationButton/useTranslation.ts`
- [ ] T031 Verify no console errors: start dev server (`npm run start` in frontend), open DevTools console, click translate, verify no JavaScript errors
- [ ] T032 Test with hot reload: while dev server running, modify backend endpoint slightly, verify hot reload works and frontend still functions
- [ ] T033 Document feature: verify comment in `/mnt/d/code/Hackathon-1/backend/app/api/v1/translate.py` explains JWT requirement
- [ ] T034 Create PR summary: document changes, reference user stories, note that authentication protection is now enforced

**Final Checkpoint**: Feature complete, tested, documented, ready for merge

---

## Execution Timeline

| Phase | Tasks | Est. Time | Notes |
|-------|-------|-----------|-------|
| Setup | T001-T003 | 5 min | Quick verification of existing structure |
| Foundational | T004-T007 | 5 min | Create backend files and register router |
| US1a | T008-T011 | 8 min | Implement core endpoint + test auth |
| US1b | T012-T015 | 5 min | Verify 401 errors and logging |
| US1c | T016-T019 | 5 min | Verify responsive design |
| US2 | T020-T023 | 5 min | Verify login prompt and flow |
| Integration | T024-T028 | 5 min | E2E testing and edge cases |
| Polish | T029-T034 | 5 min | Code review, docs, console cleanup |
| **Total** | **34 tasks** | **~43 min** | Includes all verification and testing |

**MVP Scope** (first 20 minutes):
- Complete Phase 1 (Setup)
- Complete Phase 2 (Foundational)
- Complete Phase 3 (User Story 1a: Authenticated Translation)
- This delivers: ✅ Authenticated users can translate; ✅ Backend validates JWT

**Extended Scope** (additional 10 minutes):
- Complete Phase 3 remaining (1b, 1c)
- This adds: ✅ Proper error handling; ✅ Mobile responsive

**Full Scope** (all 30 minutes):
- Complete all phases including User Story 2
- This adds: ✅ Logged-out UX; ✅ Full integration testing

---

## Parallelization Opportunities

**Can run in parallel** (different files, no dependencies):
- T001-T003: Setup tasks (1 per setup step)
- T005-T006: Backend file creation (different files)
- T008-T009: Endpoint implementation and validation (same file, sequence required)
- T010-T011: Frontend verification and manual test (different concerns)
- T012-T013: Authorization testing (different scenarios)
- T016-T017: CSS verification (different components)
- T020-T021: Component verification (different files)
- T026-T027: Error testing scenarios (different test cases)

**Sequential requirements**:
- T004 must precede T008 (need to understand existing pattern)
- T007 must precede T008 (endpoint needs to be registered)
- T008 must precede T011 (manual test needs endpoint)
- T020-T021 must precede T022 (need to verify components before testing)

---

## Testing Strategy

**No formal test files required** (per spec.md - tests are optional). Instead, use:

1. **Manual Testing** (Phase 3-5): Browser testing with curl commands provided in quickstart.md
2. **Logging Verification** (Phase 5-6): Check backend logs for auth events
3. **Console Verification** (Phase 6): DevTools console for JavaScript errors
4. **Hot Reload Verification** (Phase 6): Verify development server works correctly

**If tests needed in future**:
- Create `backend/tests/test_translate_auth.py` for JWT validation scenarios
- Create `frontend/src/components/TranslationButton/__tests__/TranslationButton.test.tsx` for component behavior
- Create integration test in backend/tests/test_translate_flow.py for full E2E flow

---

## Success Criteria (All Tasks Complete)

- ✅ T001-T007: Backend infrastructure ready
- ✅ T008-T011: Authenticated users can translate article to Urdu
- ✅ T012-T015: Backend validates JWT and rejects unauthorized requests
- ✅ T016-T019: UI responsive on mobile (320px+)
- ✅ T020-T023: Logged-out users see authentication prompt
- ✅ T024-T028: Full E2E flow works; edge cases handled
- ✅ T029-T034: Code reviewed; documented; no console errors

**Definition of Done**: All tasks checked; PR created with reference to user stories; feature works as specified

---

## File Manifest (What Gets Created/Modified)

### Created Files
- `/mnt/d/code/Hackathon-1/backend/app/api/v1/translate.py` — Translation endpoint
- `/mnt/d/code/Hackathon-1/backend/app/schemas/translate.py` — Request/response schemas

### Modified Files
- `/mnt/d/code/Hackathon-1/backend/app/main.py` — Register translate router
- `/mnt/d/code/Hackathon-1/Front-End-Book/src/components/TranslationButton/useTranslation.ts` — Verify Authorization header (may already exist)
- `/mnt/d/code/Hackathon-1/Front-End-Book/src/components/TranslationButton/index.tsx` — Verify ProtectedFeature wrapper (already in place)

### Verified Files (No Changes)
- `/mnt/d/code/Hackathon-1/backend/app/routes/auth.py` — `get_current_user()` dependency
- `/mnt/d/code/Hackathon-1/backend/app/security.py` — JWT utilities
- `/mnt/d/code/Hackathon-1/Front-End-Book/src/components/Auth/ProtectedFeature.tsx` — Component wrapper
- `/mnt/d/code/Hackathon-1/Front-End-Book/src/context/AuthContext.tsx` — Auth state
- `/mnt/d/code/Hackathon-1/Front-End-Book/src/components/TranslationButton/TranslationButton.module.css` — Styles

---

## Notes

- **No database schema changes** — Existing `users` table sufficient
- **No new external dependencies** — Uses existing FastAPI, python-jose, React
- **Frontend protection already exists** — ProtectedFeature wrapper in place; verification only
- **Backend pattern proven** — get_current_user dependency from existing auth routes
- **CORS configured** — Existing CORS middleware allows Authorization header

---

**Status**: ✅ Ready for Implementation
**Created**: 2026-02-10
**Owner**: Team
**Next Step**: Begin Phase 1 setup tasks
