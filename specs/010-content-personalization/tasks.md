---
description: "Implementation task breakdown for Content Personalization feature"
---

# Tasks: Content Personalization Based on User Background

**Input**: Design documents from `specs/010-content-personalization/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Organization**: Tasks are grouped by user story and phase to enable independent implementation and testing of each story

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup & Research (Verification)

**Purpose**: Verify infrastructure and dependencies are ready; no new code

**Expected Duration**: 30 minutes

- [x] T001 Verify OpenAI API integration pattern in backend (check requirements.txt has openai==1.14.0, confirm gpt-4o-mini model available, verify API key in config)
- [x] T002 Verify Docusaurus article DOM structure for content extraction (confirm `document.querySelector('article')` reliably finds chapter content, test on existing page)
- [x] T003 [P] Verify JWT token handling in frontend (confirm useAuth hook provides user profile data: software_background, hardware_background, learning_goal from AuthContext)
- [x] T004 [P] Verify OpenAI rate limiting handling (understand 429 status codes, confirm plan error handling per ADR-004)

---

## Phase 2: Foundational (Backend Infrastructure)

**Purpose**: Core backend infrastructure that MUST be complete before frontend can be tested

**⚠️ CRITICAL**: No frontend integration can begin until this phase is complete

- [x] T005 Create backend schema models in `backend/app/schemas/personalize.py` (PersonalizeRequest with content, hardware_background, learning_goal; PersonalizeResponse with personalized_content, personalization_level, metadata)
- [x] T006 [P] Create OpenAI service in `backend/app/services/openai_service.py` (generate_personalization_prompt function with 3 templates: beginner/intermediate/advanced; personalize_content function with error handling per ADR-004; logging)
- [x] T007 [P] Implement personalization endpoint in `backend/app/api/v1/personalize.py` (POST /api/v1/personalize with JWT validation, content validation, user profile extraction from token, OpenAI service calls, response mapping; status codes: 200/400/401/429/500)
- [x] T008 Register personalization router in `backend/app/main.py` (add `from app.api.v1 import personalize` and `app.include_router(personalize.router)`)

**Checkpoint**: Backend endpoint is fully functional and testable via curl with JWT token

---

## Phase 3: User Story 1 - Beginner Gets Simplified Content (Priority: P1) 🎯 MVP

**Goal**: Beginner-level users can click "Personalize for Me" and receive simplified content (Flesch-Kincaid 12-14) with step-by-step explanations, tips, common mistakes, and glossary links, all while preserving citations and code examples

**Independent Test Criteria**:
1. Sign in as user with `software_background: "beginner"`
2. Click "Personalize for Me" button on chapter
3. Verify content transformed to simple language with tips/mistakes/glossary
4. Verify ALL citations preserved exactly (100% match)
5. Verify ALL code examples preserved exactly (100% match)
6. Verify "Reset to Original" button works
7. Verify reading level is Flesch-Kincaid 12-14 (automated scoring)

### Implementation for User Story 1

- [x] T009 [P] Create PersonalizationButton component in `src/components/PersonalizationButton/PersonalizationButton.tsx` (states: default/loading/personalized/error; debounce rapid clicks; ProtectedFeature wrapper; hooks: useAuth, usePersonalization)
- [x] T010 [P] Create PersonalizationButton styles in `src/components/PersonalizationButton/PersonalizationButton.module.css` (44px min height button, CSS spinner animation, error message styling, mobile responsive @media, state transitions fade/slide 0.3s)
- [x] T011 [P] Create usePersonalization hook in `src/hooks/usePersonalization.ts` (useState for state/error/personalizationLevel, useRef for originalContent, personalize callback fetches article content via DOM query, POSTs to /api/v1/personalize, handles response/errors per ADR-004, resetToOriginal callback)
- [x] T012 [US1] Add PersonalizationButton to DocItem layout in `src/theme/DocItem/Layout/index.tsx` (import PersonalizationButton, render before article children at chapter start)
- [x] T013 [US1] Test beginner personalization end-to-end (manually: sign in as beginner → click button → verify simplified content → check citations/code preserved → click reset → verify original restored)

**Checkpoint**: User Story 1 is fully functional and independently testable. Beginner users can personalize any chapter and reset to original.

---

## Phase 4: User Story 2 - Advanced Gets Research-Focused Content (Priority: P1)

**Goal**: Advanced-level users with research goals can click "Personalize for Me" and receive research-focused content with optimization tips, seminal paper highlights, and hardware deployment strategies, all while preserving citations and code

**Independent Test Criteria**:
1. Sign in as user with `software_background: "advanced"` and `learning_goal: "research"`
2. Click "Personalize for Me" button on chapter
3. Verify content is concise and technical, assumes CS/robotics background
4. Verify citations are highlighted for research relevance
5. Verify optimization tips and benchmarks included
6. Verify hardware deployment emphasis (RTX/Jetson)
7. Verify ALL citations preserved exactly (100% match)
8. Verify ALL code examples preserved exactly (100% match)
9. Verify "Reset to Original" button works

### Implementation for User Story 2

- [x] T014 [US2] Test advanced personalization end-to-end (manually: sign in as advanced/research user → click button → verify technical/concise content → verify citations highlighted → check code preserved → verify hardware deployment emphasis → click reset → verify original restored)
- [x] T015 [US2] Verify citation preservation validation (run test on multiple chapters to confirm 100% of citations remain unchanged in personalized content)
- [x] T016 [US2] Verify code preservation validation (run test on chapters with code blocks to confirm 100% of code remains exactly unchanged in personalized content)

**Checkpoint**: User Story 2 is fully functional and independently testable. Advanced users receive appropriate technical depth and research focus.

---

## Phase 5: User Story 3 - Intermediate Gets Balanced Content (Priority: P2)

**Goal**: Intermediate-level users can click "Personalize for Me" and receive balanced technical content with best practices and moderate detail, with appropriate simulation/hardware balance

**Independent Test Criteria**:
1. Sign in as user with `software_background: "intermediate"` and `hardware_background: "basic"`
2. Click "Personalize for Me" button on chapter
3. Verify content uses balanced technical language (not oversimplified, not overly dense)
4. Verify best practices and optimization tips included
5. Verify simulation tools (Gazebo, Isaac Sim) emphasized
6. Verify CPU alternatives provided
7. Verify GPU upgrade path mentioned but not required
8. Verify ALL citations preserved exactly (100% match)
9. Verify ALL code examples preserved exactly (100% match)

### Implementation for User Story 3

- [x] T017 [US3] Test intermediate personalization end-to-end (manually: sign in as intermediate/basic hardware user → click button → verify balanced technical content → verify simulation-first emphasis → check code preserved → click reset → verify original restored)
- [x] T018 [US3] Test hardware-aware personalization for all contexts (test content for hardware_background: none/basic/advanced to verify cloud/simulation/deployment emphasis matches expectation)

**Checkpoint**: User Story 3 is fully functional and independently testable. Intermediate users receive balanced, hardware-appropriate content.

---

## Phase 6: User Story 4 - Hardware Context Switching (Priority: P2)

**Goal**: Users can update their hardware background and receive re-personalized content that reflects new hardware context (e.g., cloud → local GPU → deployment)

**Independent Test Criteria**:
1. Sign in, personalize content with `hardware_background: "none"` (verify cloud emphasis)
2. Update user profile to `hardware_background: "advanced"`
3. Return to chapter, click "Personalize for Me" again
4. Verify content now emphasizes hardware deployment and CUDA optimization
5. Verify previous personalization state doesn't interfere with new personalization
6. Verify "Reset to Original" always returns exact original content

### Implementation for User Story 4

- [x] T019 [US4] Test hardware context switching (manually: personalize with hardware=none → verify cloud options → update profile to hardware=advanced → re-personalize → verify hardware deployment emphasis → verify reset always returns original)
- [x] T020 [US4] Test profile update integration (verify AuthContext properly updates user profile data when user updates hardware_background)

**Checkpoint**: User Story 4 is fully functional. Users can evolve their hardware context and receive appropriate personalized content.

---

## Phase 7: User Story 5 - Learning Goals Influence Tone (Priority: P3)

**Goal**: User's learning goal (career/hobby/research) influences personalization tone and examples while preserving technical accuracy

**Independent Test Criteria**:
1. Sign in with `learning_goal: "hobby"` (verify enthusiastic tone, fun examples)
2. Sign in with `learning_goal: "career"` (verify professional tone, industry examples)
3. Sign in with `learning_goal: "research"` (verify academic tone, novel approaches)
4. Verify all three contexts preserve citations and code exactly
5. Verify tone differences are apparent while technical facts remain unchanged

### Implementation for User Story 5

- [x] T021 [US5] Test learning goal personalization for career goal (manually: sign in with learning_goal: "career" → click personalize → verify professional tone and job market relevance → verify code/citations preserved)
- [x] T022 [US5] Test learning goal personalization for hobby goal (manually: sign in with learning_goal: "hobby" → click personalize → verify enthusiastic tone and fun examples → verify code/citations preserved)
- [x] T023 [US5] Test learning goal personalization for research goal (manually: sign in with learning_goal: "research" → click personalize → verify academic tone and novel approaches → verify code/citations preserved)

**Checkpoint**: User Story 5 is fully functional. Learning goals appropriately influence personalization tone while maintaining technical integrity.

---

## Phase 8: Error Handling & Edge Cases

**Purpose**: Verify all error scenarios from ADR-004 are handled gracefully

- [x] T024 [P] Test OpenAI timeout (simulate API delay > 10s, verify error message displayed, original content intact, user can reset/retry)
- [x] T025 [P] Test invalid JWT (call endpoint with expired token, verify 401 redirect to signin with message)
- [x] T026 [P] Test network error (simulate connection loss during personalization, verify user-friendly error message, retry option works)
- [x] T027 [P] Test empty content (navigate to page without article element, verify "No content found" error)
- [x] T028 [P] Test rate limiting (rapid personalization requests, verify 429 handling with retry message)
- [x] T029 [P] Test malformed OpenAI response (mock invalid API response, verify "Transformation failed" error with fallback to original)

**Checkpoint**: All error scenarios handled per ADR-004 with user-friendly messages and graceful fallbacks

---

## Phase 9: Performance & Mobile Testing

**Purpose**: Verify non-functional requirements and mobile responsiveness

- [x] T030 [P] Performance verification (measure: personalization completes < 8 seconds end-to-end, state transitions < 200ms, content replacement instant, no UI jank)
- [x] T031 [P] Mobile responsiveness testing (iOS Safari: button visible/clickable, loading spinner works, content readable, reset accessible; Android Chrome: same verification)
- [x] T032 [P] Rapid click debouncing (verify only one request sent when clicking button multiple times within 300ms)

**Checkpoint**: All performance metrics met, mobile UX acceptable on iOS and Android

---

## Phase 10: Constitutional Alignment & Content Preservation Validation

**Purpose**: Verify feature meets all constitutional requirements and content preservation guarantees

- [x] T033 Progressive learning verification (verify beginner content is simpler than intermediate which is simpler than advanced, proper reading level scoring)
- [x] T034 Citation preservation audit (run automated validation: parse all IEEE citations in original → verify 100% preserved in all personalization levels)
- [x] T035 Code preservation audit (run automated validation: extract all code blocks → verify 100% byte-for-byte match in all personalization levels)
- [x] T036 Technical facts accuracy (manually verify: no technical facts were changed, version numbers preserved, APIs unchanged, safety protocols unchanged)
- [x] T037 Feature protection audit (verify: unauthenticated users don't see button, endpoint rejects requests without JWT, no profile data leakage)

**Checkpoint**: Feature fully complies with constitutional requirements; all content preservation guarantees verified

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements and documentation

- [x] T038 [P] Add component export in `src/components/PersonalizationButton/index.ts` (export PersonalizationButton component)
- [x] T039 [P] Add hook export in `src/hooks/index.ts` (export usePersonalization hook)
- [x] T040 [P] Documentation: Add inline code comments to PersonalizationButton.tsx explaining state machine and debouncing logic
- [x] T041 [P] Documentation: Add inline code comments to usePersonalization.ts explaining DOM extraction and error handling
- [x] T042 [P] Documentation: Add inline code comments to openai_service.py explaining prompt template structure and preservation constraints
- [x] T043 [P] Documentation: Add inline code comments to personalize.py endpoint explaining validation, user profile extraction, and error responses
- [x] T044 Run end-to-end feature validation (sign in as all three user types → personalize all available chapters → verify all combinations work correctly)

**Checkpoint**: Feature complete, documented, and ready for production

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately (30 min)
- **Foundational Backend (Phase 2)**: Depends on Setup completion - BLOCKS all frontend work (expected: 1 hour after Phase 1)
- **User Stories (Phase 3+)**: Can start AFTER Foundational Backend is complete and testable via curl
  - US1 & US2 can proceed in parallel (different frontend components, both use same backend endpoint)
  - US3 depends only on Foundational, independent of US1/US2
  - US4 depends only on Foundational, independent of others
  - US5 depends only on Foundational, independent of others
- **Error Handling (Phase 8)**: Depends on at least US1 complete (have working backend/frontend)
- **Performance/Mobile (Phase 9)**: Depends on Error Handling complete
- **Constitutional Validation (Phase 10)**: Depends on all user stories complete
- **Polish (Phase 11)**: Depends on all previous phases complete

### User Story Dependencies

- **US1 (Beginner)**: Depends on Foundational Backend (Phase 2) only
- **US2 (Advanced)**: Depends on Foundational Backend (Phase 2) only - can run PARALLEL with US1
- **US3 (Intermediate)**: Depends on Foundational Backend (Phase 2) only - can run PARALLEL with US1/US2
- **US4 (Hardware Switching)**: Depends on Foundational Backend + at least one story implemented (recommend after US1)
- **US5 (Learning Goals)**: Depends on Foundational Backend + at least one story implemented (recommend after US1)

### Within Each Phase

- Tests MUST be in test form (failing) before implementation
- Models before services before endpoints
- Core implementation before integration
- Each story complete before moving to next priority

### Parallel Opportunities

**After Phase 1 (Setup) is complete:**
- All Phase 2 (Foundational Backend) tasks marked [P] can run in parallel:
  - T005: Create schema models
  - T006: Create OpenAI service (uses schemas from T005, but different concern)
  - T007: Create personalization endpoint (uses schemas/service from T005/T006, but different task)
  - T008: Register router (must wait for T007 complete, is single task)

**After Phase 2 (Foundational Backend) is complete:**
- User Stories 1, 2, 3 can be implemented in parallel by different developers:
  - Developer A: US1 (T009-T013) - Beginner content
  - Developer B: US2 (T014-T016) - Advanced content validation
  - Developer C: US3 (T017-T018) - Intermediate content
- T009, T010, T011 within US1 can run in parallel (different components)

**After US1 is complete:**
- US4 (T019-T020) can start (depends on user profile updates working)
- US5 (T021-T023) can start (depends on learning goal context being used)

---

## Parallel Example: Optimal 2-Developer Workflow

```
Developer A                           Developer B
============                          ============

Phase 1: Setup & Research (30 min, both)
├─ T001-T004 (parallel)

Phase 2: Foundational Backend (1 hour, can split)
├─ T005-T007 (A): Schemas, Services, Endpoint (parallel)
└─ T008 (B): Router registration

Phase 3-5: User Stories (parallel, ~2 hours total)
├─ Developer A: US1 (T009-T013) - Frontend Button
│   └─ T009-T011 parallel (components), T012-T013 sequential
└─ Developer B: US2+US3 validation (T014-T018)
    └─ T014-T018 sequential (validation tests)

After US1 complete:
├─ Developer A: US4 (T019-T020) - Hardware switching
└─ Developer B: US5 (T021-T023) - Learning goals

Phase 8-11: Final validation & polish
├─ T024-T029 (Error handling, parallel)
├─ T030-T032 (Performance/Mobile, parallel)
├─ T033-T037 (Constitutional validation, parallel)
└─ T038-T044 (Polish, parallel where marked [P])

Total Estimated Time: 4-5 hours (serial), 2.5-3 hours (parallel with 2 devs)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup & Research (30 min)
2. Complete Phase 2: Foundational Backend (1 hour) - **CRITICAL PATH**
3. Complete Phase 3: User Story 1 (45 min) - Frontend button + integration
4. **STOP and VALIDATE**:
   - Sign in as beginner → Click button → Verify simplified content
   - Verify citations preserved
   - Verify code preserved
   - Verify reset works
5. Deploy MVP if ready (users can personalize for beginner level)

**MVP Scope Task Count**: T001-T013 = 13 tasks, ~2.25 hours

### Incremental Delivery (Recommended Hackathon Strategy)

1. Complete Phases 1-3 (Setup + Foundational + US1) → MVP ready (~2.25 hours)
2. Add Phases 4-5 (US2 + US3 validation) → All skill levels supported (~1 hour)
3. Add Phase 6 (US4: Hardware switching) → Dynamic personalization (~30 min)
4. Add Phase 7 (US5: Learning goals) → Tone personalization (~30 min)
5. Add Phase 8 (Error Handling) → Production-ready (~45 min)
6. Add Phase 9-11 (Performance + Polish) → Complete feature (~1.5 hours)

**Full Feature Task Count**: T001-T044 = 44 tasks, ~5-6 hours total

### Priority Levels for Time Constraints

- **0.5 Hour**: T001-T004 (Setup) - Just verify, no coding
- **1.5 Hours**: + T005-T008 (Backend) - Endpoint working
- **2.25 Hours**: + T009-T013 (US1) - MVP working (beginner personalization)
- **3 Hours**: + T014-T018 (US2+US3) - All skill levels
- **3.75 Hours**: + T019-T020 (US4) - Dynamic hardware context
- **4.5 Hours**: + T021-T023 (US5) - Learning goal personalization
- **5.25 Hours**: + T024-T029 (Error Handling) - Robust error recovery
- **5.75 Hours**: + T030-T032 (Performance) - Meets performance targets
- **6.5 Hours**: + T033-T044 (Constitutional + Polish) - Complete, production-ready

---

## Notes

- [P] tasks = different files, no dependencies on this phase's blocking tasks
- [Story] label maps task to specific user story for traceability (US1-US5)
- Each user story should be independently completable and testable after Foundational phase
- Constitutional alignment must be verified for all personalization outputs
- Content preservation (citations, code, facts) is non-negotiable - 100% accuracy required
- Commit after each phase or logical group (after T008, T013, T018, T020, T023, T029, T032, T037, T044)
- Stop at any checkpoint to validate story independently before proceeding to next story
- Mobile testing critical - feature must work equally well on iOS/Android
- Error handling comprehensive per ADR-004 - all 6 error scenarios must be tested
- Constitutional requirements must be met - no content corruption allowed
