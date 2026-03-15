# Implementation Tasks: Urdu Translation Feature

**Feature**: Add "Translate to Urdu 🌐" button to each chapter in Modules 1-4
**Branch**: `006-urdu-translation`
**Spec**: [specs/006-urdu-translation/spec.md](spec.md)
**Plan**: [specs/006-urdu-translation/plan.md](plan.md)
**Date**: 2026-02-04

---

## Task Overview

| Phase | Title | Task Count | Priority | Status |
|-------|-------|-----------|----------|--------|
| 1 | Setup & Infrastructure | 3 | P0 | Pending |
| 2 | Foundational (Blocking) | 5 | P0 | Pending |
| 3 | US1: Translate Chapter to Urdu | 8 | P1 | Pending |
| 4 | US2: Persist Translation Preference | 4 | P2 | Pending |
| 5 | US3: Consistent Translation Quality | 3 | P2 | Pending |
| 6 | Polish & Cross-Cutting | 4 | P3 | Pending |
| | **TOTAL** | **27** | | |

---

## Dependencies & Execution Strategy

### Task Dependency Graph

```
Phase 1 (Setup)
  ↓
Phase 2 (Foundational - Blocking)
  ├→ Phase 3 (US1: Core Translation) [INDEPENDENT]
  ├→ Phase 4 (US2: Preference Persistence) [INDEPENDENT from US3]
  └→ Phase 5 (US3: Translation Quality) [INDEPENDENT]
       ↓
Phase 6 (Polish & Cross-Cutting)
```

### Parallel Execution Opportunities

**US1 and US2 can run in PARALLEL** after Phase 2:
- US1: Focuses on button UI, API integration, rendering
- US2: Focuses on localStorage, state management
- No shared component dependencies until Phase 6

**US1 and US3 can run in PARALLEL**:
- US1: Feature implementation
- US3: Quality validation and testing (can be done as feature work)

### MVP Scope (Recommended)

**Minimum Viable Product**: Complete Phase 1 + Phase 2 + Phase 3 (US1 only)
- Delivers: Working translation button with English→Urdu toggle on all chapters
- Estimated scope: Tasks T001-T015 (~3-4 days)
- Value: Core feature working, users can translate chapters
- Follow-up: Add US2 (persistence) and US3 (quality) in subsequent phases

---

## Phase 1: Setup & Infrastructure

### Phase Goal
Initialize project structure, install dependencies, and configure OpenAI API integration for MVP (client-side approach).

### Independent Test Criteria
- ✅ Environment configured with REACT_APP_OPENAI_API_KEY
- ✅ OpenAI JS SDK imports successfully
- ✅ Docusaurus dev server starts without errors
- ✅ Component directory structure matches plan.md

---

- [ ] T001 Install OpenAI JS SDK in Front-End-Book project via npm install openai@^4.x

- [ ] T002 Create component directory structure in Front-End-Book/src/components/TranslationButton/ with files: TranslationButton.tsx, TranslationButton.module.css, types.ts, useTranslation.ts and folder __tests__/

- [ ] T003 Create utility directory structure in Front-End-Book/src/utils/ with files: translationApi.ts, contentParser.ts, storageManager.ts

---

## Phase 2: Foundational (Blocking)

### Phase Goal
Build foundational utilities and type definitions that all user stories depend on. Must complete before feature development.

### Independent Test Criteria
- ✅ All TypeScript types defined and importable
- ✅ translationApi.ts exports translate() function signature
- ✅ contentParser.ts exports parseChapterContent() function
- ✅ storageManager.ts exports localStorage read/write functions
- ✅ No compilation errors with strict TypeScript

---

- [ ] T004 Define TypeScript types in Front-End-Book/src/components/TranslationButton/types.ts including: TranslationPreference (language: 'en'|'ur', savedAt, source), TranslationState (language, isLoading, error, translatedText), TranslationError, TranslationResponse

- [ ] T005 [P] Create OpenAI API wrapper in Front-End-Book/src/utils/translationApi.ts with function: translate(content: string, targetLanguage: 'ur'): Promise<string> including error handling, retry logic with exponential backoff, system prompt for code preservation

- [ ] T006 [P] Create content parser in Front-End-Book/src/utils/contentParser.ts with function: parseChapterContent(articleElement: HTMLElement): {prose: string, codeBlocks: CodeBlock[]} to extract translatable text while preserving code blocks

- [ ] T007 [P] Create localStorage manager in Front-End-Book/src/utils/storageManager.ts with functions: getPreference(), setPreference(language), hasLocalStorage(), with fallback to session-only storage when localStorage unavailable

- [ ] T008 Create custom hook useTranslation() in Front-End-Book/src/components/TranslationButton/useTranslation.ts to manage translation state (language, isLoading, error), provide translate() and toggleLanguage() actions, load/save preference

---

## Phase 3: US1 - Translate Chapter to Urdu (P1)

### Phase Goal
Implement core translation feature: button appears on chapters, clicking translates English→Urdu, content toggles back to English. Formatting and code blocks preserved.

### Story Dependencies
- ✅ All Phase 2 tasks completed

### Independent Test Criteria
- ✅ Translation button appears at top of every chapter in Modules 1-4
- ✅ Clicking button triggers translation API call
- ✅ Translated Urdu text renders in place of English
- ✅ Code blocks, headings, lists remain unchanged during translation
- ✅ Clicking button again toggles back to English
- ✅ Translation completes within 3 seconds
- ✅ Error messages display if API fails

---

- [ ] T009 [P] [US1] Create TranslationButton component in Front-End-Book/src/components/TranslationButton/TranslationButton.tsx rendering button with label "Translate to Urdu 🌐", loading state indicator, error message display, and integration with useTranslation hook

- [ ] T010 [P] [US1] Create component styles in Front-End-Book/src/components/TranslationButton/TranslationButton.module.css with button styling, hover/active states, loading spinner animation, error message styling, responsive design for mobile/tablet/desktop

- [ ] T011 [US1] Integrate useTranslation() hook in TranslationButton component: destructure language, isLoading, error, toggleLanguage from hook; manage component lifecycle

- [ ] T012 [P] [US1] Implement translation trigger logic in TranslationButton: On button click, call toggleLanguage() action, display loading spinner, handle translation response, re-render translated content on success, display error message on failure

- [ ] T013 [US1] Modify Docusaurus theme to inject TranslationButton: Swizzle DocSidebar.tsx in Front-End-Book/src/theme/DocSidebar.tsx or equivalent chapter wrapper component to render <TranslationButton /> above article content

- [ ] T014 [P] [US1] Add content state management in useTranslation hook: Store original English content in state before translation, restore on toggle back to English, preserve code block content throughout lifecycle

- [ ] T015 [US1] Manual testing across all Modules 1-4: Select minimum 2 chapters per module, verify translation works, formatting preserved, code blocks unchanged, toggle back to English works, translation completes in <3 seconds

- [ ] T016 [US1] Implement error boundary and error handling in Front-End-Book/src/components/TranslationButton/ErrorBoundary.tsx: Catch component errors gracefully, display user-friendly error messages, prevent feature from breaking page

---

## Phase 4: US2 - Persist Translation Preference (P2)

### Phase Goal
Save user's language preference (English/Urdu) to localStorage. Automatically apply preference when user returns to site or navigates between chapters.

### Story Dependencies
- ✅ Phase 2 tasks completed
- ⚠️ Can run in PARALLEL with US1 (after Phase 2)

### Independent Test Criteria
- ✅ When user selects Urdu, preference is saved to localStorage with timestamp
- ✅ When user returns to site, preference is loaded and chapter auto-translates
- ✅ When user navigates to new chapter within session, preference is applied automatically
- ✅ When user toggles language, preference is updated in localStorage
- ✅ If localStorage is unavailable, translation still works (preference not saved)
- ✅ If localStorage is corrupted, fallback to English with valid timestamp

---

- [ ] T017 [P] [US2] Extend storageManager.ts with functions: loadPreferenceOnMount() to initialize preference from localStorage on app start, watchPreferenceChanges() to subscribe to preference updates

- [ ] T018 [US2] Add preference initialization in useTranslation() hook: Load preference from storageManager on mount, initialize language state based on saved preference or default to 'en', handle corrupted data by fallback to English

- [ ] T019 [P] [US2] Implement auto-translate on mount in TranslationButton: If saved preference is 'ur', automatically trigger translation after chapter article element loads (useEffect dependency on article selector)

- [ ] T020 [US2] Add preference persistence to toggleLanguage() action in useTranslation hook: When language changes, call storageManager.setPreference() with new language and current ISO8601 timestamp

---

## Phase 5: US3 - Consistent Translation Quality (P2)

### Phase Goal
Validate translation quality, preserve technical terminology, and ensure code examples remain unchanged during translation.

### Story Dependencies
- ✅ Phase 2 tasks completed
- ✅ Phase 3 (US1) tasks T009-T012 for translation logic
- ⚠️ Can run in PARALLEL with US1/US2 for QA testing

### Independent Test Criteria
- ✅ Code blocks remain completely unchanged after translation
- ✅ Technical terms (ROS2, Virtual Machine, etc.) are correctly translated or preserved
- ✅ Headings, lists, and prose structure preserved
- ✅ Urdu text renders correctly across browsers (Chrome, Firefox, Safari)
- ✅ Special Unicode characters (Urdu script) display properly
- ✅ Translation accuracy validated against human-reviewed baseline (95% match)

---

- [ ] T021 [P] [US3] Create content validation test in Front-End-Book/src/components/TranslationButton/__tests__/contentValidation.test.ts: Unit tests asserting code blocks unchanged, technical terms preserved, Urdu character set valid, Urdu font renders

- [ ] T022 [US3] Create Urdu rendering test in Front-End-Book/src/components/TranslationButton/__tests__/urduRendering.test.ts: Integration tests for Urdu text on DOM, no encoding issues, correct script direction, Unicode preservation

- [ ] T023 [US3] Create manual quality review checklist in specs/006-urdu-translation/QUALITY_CHECKLIST.md: Steps to validate translated chapters against human-reviewed baseline, accuracy validation process (target 95% match), technical term verification

---

## Phase 6: Polish & Cross-Cutting Concerns

### Phase Goal
Final polish, documentation, testing, and deployment readiness. Handle edge cases and ensure feature meets all success criteria.

### Independent Test Criteria
- ✅ All 23 MVP tasks completed and passing
- ✅ End-to-end test: User journey from chapter view → translate → toggle → navigate → preference persists
- ✅ Performance: Translation completes <3 seconds, button click <100ms perceived latency
- ✅ Accessibility: Button keyboard-accessible, ARIA labels present, screen reader compatible
- ✅ Documentation: README updated, user guide created
- ✅ Deployment: Build passes npm run build, no console errors in production build

---

- [ ] T024 [P] Create end-to-end test in Front-End-Book/src/components/TranslationButton/__tests__/e2e.test.ts: Full user journey - load chapter → translate to Urdu → verify content changed → toggle to English → verify restored → navigate to different chapter → verify preference auto-applied

- [ ] T025 [P] Performance and accessibility test: Benchmark translation API response time (target <3 seconds), button click latency (target <100ms), verify keyboard accessibility (Tab navigation, Enter/Space activation), add ARIA labels aria-label="Translate to Urdu" and aria-pressed

- [ ] T026 Create user documentation in specs/006-urdu-translation/USER_GUIDE.md: How to use translation feature, browser requirements, troubleshooting common issues, supported languages, performance expectations

- [ ] T027 Update project documentation: Add translation feature to Front-End-Book README.md, link to quickstart guide, add section in specs/006-urdu-translation/DEPLOYMENT.md for production deployment considerations

---

## Success Criteria Validation

### All Functional Requirements (FR)

- [ ] **FR-001**: Button visible on every chapter in Modules 1-4 (T009, T013, T015)
- [ ] **FR-002**: Clicking button translates to Urdu via OpenAI GPT-4 (T012, T005)
- [ ] **FR-003**: Formatting preserved (headings, code, lists) (T006, T021, T015)
- [ ] **FR-004**: Toggle between English and Urdu (T012, T014)
- [ ] **FR-005**: Preference stored in localStorage (T017, T020)
- [ ] **FR-006**: Preference auto-applied on return and navigation (T018, T019)
- [ ] **FR-007**: Loading indicator displayed (T009, T010)
- [ ] **FR-008**: Errors handled gracefully (T012, T016)
- [ ] **FR-009**: Code blocks unchanged (T006, T021)
- [ ] **FR-010**: Applied to all .md/.mdx in Modules 1-4 (T013, T015)

### All Success Criteria (SC)

- [ ] **SC-001**: Button visible on every chapter (T009, T013, T015)
- [ ] **SC-002**: Translation completes <3 seconds (T025, T024)
- [ ] **SC-003**: 95% content translated accurately (T023, T022)
- [ ] **SC-004**: Preference persists across sessions (T017, T020, T024)
- [ ] **SC-005**: Code blocks preserved (T006, T021, T015)
- [ ] **SC-006**: Errors handled gracefully (T016, T024, T025)

---

## Implementation Quick Start

```bash
# Setup
git checkout 006-urdu-translation
npm install  # Includes openai@^4.x (T001)

# Configure environment
export REACT_APP_OPENAI_API_KEY=<your-openai-api-key>

# Start dev server
npm start

# Begin implementation in order:
# Phase 1: T001-T003 (Setup)
# Phase 2: T004-T008 (Foundational)  
# Phase 3: T009-T016 (US1 - Core feature, MVP scope)
# Phase 4: T017-T020 (US2 - Persistence, optional)
# Phase 5: T021-T023 (US3 - Quality, optional)
# Phase 6: T024-T027 (Polish)
```

### MVP Completion Milestone

Complete through **T015** for working MVP (Phase 1 + 2 + 3):
- Users can click button and translate chapters
- Content toggles back to English
- All formatting preserved
- Estimated: 3-4 days

### Full Feature Completion

Complete all **T001-T027** for production-ready feature:
- Persistence, auto-translation on return
- Quality validation, Urdu rendering tests
- Documentation, accessibility, performance validation
- Estimated: 5-6 days

---

## Notes

- All file paths are relative to repo root `/mnt/d/code/Hackathon-1/`
- Tasks marked [P] can run in parallel (different files, no blocking dependencies)
- Tasks marked [US#] belong to specific user story phase
- Test any completed task by running: `npm test -- --testPathPattern=filename`
- Reference contracts in `specs/006-urdu-translation/contracts/` for API specs
