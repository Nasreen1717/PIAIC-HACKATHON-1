# Tasks: Urdu Translation Feature

**Input**: Design documents from `/specs/006-urdu-translation/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Organization**: Tasks grouped by user story (P1, P2, P2) to enable independent, parallel implementation

**Tests**: No unit tests requested in spec; integration/acceptance tests included in each user story phase

---

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: User story label (US1, US2, US3) - ONLY in user story phases
- All paths absolute or relative to `Front-End-Book/`

---

## Phase 1: Setup (Project Infrastructure)

**Purpose**: Initialize project dependencies and file structure for translation feature

- [ ] T001 Install OpenAI JavaScript SDK in Front-End-Book via `npm install openai`
- [ ] T002 Create component directory structure: `mkdir -p src/components/TranslationButton/__tests__` and `mkdir -p src/utils/`
- [ ] T003 [P] Create `.env.local` template with `REACT_APP_OPENAI_API_KEY` placeholder for development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities and infrastructure required by all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase completes

- [ ] T004 Create storage utility: `Front-End-Book/src/utils/storageManager.ts` (localStorage wrapper with try-catch error handling, fallback to session storage)
- [ ] T005 [P] Create content parser utility: `Front-End-Book/src/utils/contentParser.ts` (parseChapterContent function: extract prose + code blocks from article DOM)
- [ ] T006 [P] Create OpenAI API wrapper: `Front-End-Book/src/utils/translationApi.ts` (translateContent function calling openai.chat.completions, handle errors/retries)
- [ ] T007 Create TypeScript types file: `Front-End-Book/src/components/TranslationButton/types.ts` (TranslationError, TranslationState, TranslationPreference interfaces)
- [ ] T008 Swizzle Docusaurus DocSidebar component via `npm run swizzle @docusaurus/preset-classic DocSidebar -- --typescript` (creates `src/theme/DocSidebar.tsx`)

**Checkpoint**: All foundational utilities ready - user stories can now proceed in parallel

---

## Phase 3: User Story 1 - Translate Chapter to Urdu (Priority: P1) 🎯 MVP

**Goal**: Users can click "Translate to Urdu 🌐" button and see chapter content translated to Urdu with formatting preserved, code blocks unchanged

**Independent Test**:
1. Load any chapter in Modules 1-4
2. Click "Translate to Urdu 🌐" button at top
3. Verify: chapter prose appears in Urdu within 3 seconds (SC-002)
4. Verify: headings, lists, links remain formatted (FR-003)
5. Verify: code blocks unchanged (FR-009)
6. Click button again → content reverts to English
7. **PASS**: Chapter fully translatable and toggleable

### Implementation for User Story 1

- [ ] T009 [P] [US1] Create TranslationButton component: `Front-End-Book/src/components/TranslationButton/TranslationButton.tsx`
  - Render button with icon "🌐" and label "Translate to Urdu"
  - Implement click handler: extract article content, call translateContent(), update DOM
  - Handle loading state (show spinner, disable button)
  - Handle errors gracefully (display error message with retry option)
  - Toggle button label between "Translate to Urdu" and "Back to English"

- [ ] T010 [P] [US1] Create CSS module: `Front-End-Book/src/components/TranslationButton/TranslationButton.module.css`
  - Button styling: gradient background (purple), hover effects, disabled state
  - Spinner animation for loading state
  - Error alert styling (red background, clear error message)
  - Ensure RTL text rendering works (optional: `direction: rtl` rule)

- [ ] T011 [P] [US1] Create component index: `Front-End-Book/src/components/TranslationButton/index.ts` (export TranslationButton)

- [ ] T012 [US1] Integrate TranslationButton into swizzled DocSidebar: `Front-End-Book/src/theme/DocSidebar.tsx`
  - Import TranslationButton from components
  - Inject button at top of article content (before DocSidebar component)
  - Verify button appears only on chapter pages (not on homepage, sidebar, etc.)

- [ ] T013 [US1] Test button rendering and basic functionality (manual):
  - Navigate to chapter in Modules 1-4
  - Verify button visible with correct label and icon
  - Verify button click triggers loading state
  - Verify API call is made (check browser network tab for OpenAI request)
  - Verify response renders as Urdu text
  - Verify code blocks remain unchanged

- [ ] T014 [US1] Test error handling (manual edge cases):
  - Set invalid API key in .env.local → verify error message displays
  - Simulate network timeout → verify user-friendly error message and retry option
  - Clear chapter content (empty article) → verify graceful error
  - Test with real chapter content → verify translation completes in <3 seconds

**Checkpoint**: User Story 1 complete - Chapter translation fully functional and independently testable ✅

---

## Phase 4: User Story 2 - Persist Translation Preference (Priority: P2)

**Goal**: Users' language preference is saved to localStorage and automatically restored on page reload and when navigating between chapters

**Independent Test**:
1. Load chapter 1, click "Translate to Urdu 🌐" → content shown in Urdu
2. Navigate to chapter 2 → **VERIFY**: Content automatically displays in Urdu (no button click needed)
3. Reload browser (Ctrl+R or Cmd+R) → **VERIFY**: Chapter 1 still displays in Urdu
4. Close browser entirely, reopen site, navigate to any chapter → **VERIFY**: Default language is Urdu (preference restored)
5. Click "Back to English" → preference updates to English
6. **PASS**: Preference persists across sessions and chapters

### Implementation for User Story 2

- [ ] T015 [P] [US2] Implement preference persistence in TranslationButton: `Front-End-Book/src/components/TranslationButton/TranslationButton.tsx`
  - On component mount: Load language preference from localStorage via StorageManager
  - Set initial state to saved preference (default: 'en' if not found)
  - On translation toggle: Save new preference to localStorage immediately
  - Handle localStorage unavailable gracefully (warn user, preference resets on page reload)

- [ ] T016 [US2] Create preference auto-apply logic: `Front-End-Book/src/components/TranslationButton/TranslationButton.tsx`
  - On component mount: Check if language preference is 'ur'
  - If yes: Auto-translate chapter content immediately (no button click required)
  - Show loading state during auto-translation
  - Handle auto-translation errors same as manual translation

- [ ] T017 [US2] Test preference persistence (manual):
  - Load chapter, click "Translate to Urdu 🌐"
  - Open browser DevTools → Application tab → LocalStorage
  - Verify `translationLanguage: ur` is saved
  - Navigate to different chapter → verify content auto-translates to Urdu
  - Reload page → verify preference persists and content is in Urdu
  - Close browser tab, reopen site → verify preference still restored

- [ ] T018 [US2] Test localStorage unavailable scenario (manual):
  - Open DevTools → Application tab → disable LocalStorage (or use private browsing)
  - Click "Translate to Urdu 🌐" → verify translation works
  - Check console for warning message about localStorage unavailable
  - Navigate to different chapter → verify content reverts to English (no persistence)
  - Reload page → verify reverts to English (no preference saved)

- [ ] T019 [US2] Integrate with US1: Ensure both stories work together
  - Navigate chapter with Urdu preference saved → verify auto-translate works
  - Toggle back to English → verify button label changes and content reverts
  - Toggle to Urdu again → verify button label changes and preference saved

**Checkpoint**: User Stories 1 AND 2 complete - Translation with preference persistence fully functional ✅

---

## Phase 5: User Story 3 - Consistent Translation Quality (Priority: P2)

**Goal**: Ensure translations are accurate, technical terms are handled correctly, and code examples remain unchanged

**Independent Test**:
1. Translate chapter with code examples (e.g., Chapter 1 with Python code)
2. Verify: Code blocks display unchanged in original language/format
3. Verify: Technical terms (ROS 2, node, topic) translated appropriately to Urdu
4. Verify: Specialized concepts maintain clarity (e.g., "Virtual Machine" → translates correctly)
5. Verify: Syntax highlighting still works on code blocks
6. Manual review: Translation reads naturally and maintains educational tone
7. **PASS**: Quality baseline met (95% accuracy per SC-003)

### Implementation for User Story 3

- [ ] T020 [P] [US3] Refine OpenAI prompt for domain accuracy: `Front-End-Book/src/utils/translationApi.ts`
  - Update system prompt to emphasize technical term handling
  - Prompt should include: "On first occurrence of technical terms, provide Urdu translation with English term in parentheses"
  - Prompt should include: "Preserve ROS 2 concepts, code syntax, and educational tone"

- [ ] T021 [US3] Test code block preservation (manual validation):
  - Translate Chapter 1 (contains Python code examples)
  - Verify each code block:
    - Syntax highlighting preserved
    - No translation of code keywords (def, return, print, etc.)
    - No translation of variable names or strings
    - Code remains executable/readable
  - Repeat for different chapter with different language (bash, shell commands, etc.)

- [ ] T022 [US3] Validate technical term translation (manual review):
  - Extract 10-15 technical terms from translated chapters (ROS 2, topic, service, node, etc.)
  - Compare against Urdu robotics glossary or domain expert review
  - Verify consistency: same term always translates the same way across chapters
  - Document any inconsistencies or improvements needed

- [ ] T023 [US3] Test special characters and unicode rendering (manual, browser testing):
  - Translate chapter with special characters ((), [], {}, code fence markers)
  - Verify Urdu text renders correctly with diacritics (ِ ُ َ ً ٌ)
  - Test across browsers: Chrome, Firefox, Safari, Edge
  - Verify no broken characters or rendering issues
  - Verify RTL (right-to-left) text layout renders correctly

- [ ] T024 [US3] Manual QA with sample chapters (human review):
  - Select 3 representative chapters from Modules 1-4 (beginner, intermediate, advanced)
  - Have Urdu-speaking reviewer check:
    - Translation accuracy (95% target per SC-003)
    - Educational tone maintained
    - Technical accuracy
    - Clarity for learners
  - Document feedback and any corrections needed
  - Re-translate if accuracy <95% and revise prompt if needed

- [ ] T025 [US3] Integration test: All user stories together
  - Verify US1 (translate chapter) + US2 (preference persistence) + US3 (quality) work together
  - Test full user flow: load chapter → auto-translate (US2) → verify quality (US3) → toggle back (US1)
  - Verify no regressions or conflicts between stories

**Checkpoint**: All User Stories 1, 2, 3 complete - Feature fully functional with quality baseline met ✅

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Refinements, testing, and documentation

- [ ] T026 [P] Run quickstart guide validation: Follow all steps in `specs/006-urdu-translation/quickstart.md` to verify developer setup works end-to-end
- [ ] T027 [P] Add inline code comments to complex utilities:
  - `src/utils/translationApi.ts` - document OpenAI API integration and error handling
  - `src/utils/contentParser.ts` - document DOM parsing algorithm and code block extraction
  - `src/components/TranslationButton/TranslationButton.tsx` - document state management and event flow

- [ ] T028 Create TESTING.md in `specs/006-urdu-translation/` documenting:
  - Manual testing checklist (all acceptance scenarios from spec.md)
  - Browser compatibility testing (Chrome, Firefox, Safari, Edge)
  - Performance testing (measure translation latency, localStorage access time)
  - Error scenario testing (network off, API key invalid, localStorage disabled)
  - Urdu quality validation process

- [ ] T029 [P] Accessibility audit:
  - Verify button has `aria-label` attribute
  - Test keyboard navigation (Tab to button, Enter to activate)
  - Verify loading state announced to screen readers (`role="status"`, `aria-live="polite"`)
  - Verify error messages announced (`role="alert"`, `aria-live="assertive"`)
  - Test with screen reader (NVDA or VoiceOver)

- [ ] T030 Performance optimization (if needed):
  - Profile translation API call latency
  - If >3 seconds: Implement request debouncing (500ms minimum between API calls)
  - If localStorage slow: Consider in-memory cache as fallback
  - Benchmark browser to ensure <100ms button interaction latency

- [ ] T031 [P] Build and deploy validation:
  - Run `npm run build` to create production build
  - Verify no build errors or warnings
  - Verify translation feature works in built version (not just dev server)
  - Run `npm run serve` and test manually
  - Verify feature ready for production deployment

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends On | Notes |
|-------|-----------|-------|
| Phase 1: Setup | None | Can start immediately ✓ |
| Phase 2: Foundational | Phase 1 | BLOCKS all user stories - must complete first |
| Phase 3: User Story 1 | Phase 2 | Can start after Foundational; MVP scope |
| Phase 4: User Story 2 | Phase 2 | Can start after Foundational; integrates with US1 |
| Phase 5: User Story 3 | Phase 2 | Can start after Foundational; integrates with US1 |
| Phase 6: Polish | Phases 3-5 | All user stories should be complete |

### User Story Independence

- **User Story 1** (P1): Core feature - fully independent, can be deployed alone as MVP
- **User Story 2** (P2): Preference persistence - integrates with US1 but independently testable
- **User Story 3** (P2): Quality validation - integrates with US1 but independently testable

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks can run sequentially (quick setup)

**Phase 2 (Foundational)**: All tasks can run in parallel (different files):
- T004: storageManager.ts
- T005: contentParser.ts (independent of T004)
- T006: translationApi.ts (independent of T004, T005)
- T007: types.ts (independent)
- T008: swizzle DocSidebar (independent)

**Phase 3 (User Story 1)**: All tasks can run in parallel until integration:
- T009: TranslationButton.tsx (parallel with T010, T011)
- T010: TranslationButton.module.css (parallel with T009, T011)
- T011: index.ts (parallel with T009, T010)
- T012: Integrate into DocSidebar (depends on T009, T008)
- T013: Manual testing (depends on T012)
- T014: Error handling tests (depends on T012)

**Phase 4 (User Story 2)**: Sequential within story (depends on US1):
- T015: Add persistence logic to TranslationButton (depends on T009)
- T016: Auto-apply logic (depends on T015)
- T017: Manual testing (depends on T016)
- T018: localStorage unavailable testing (depends on T016)
- T019: Integration with US1 (depends on T009, T016)

**Phase 5 (User Story 3)**: Sequential within story (depends on US1):
- T020: Refine prompt (depends on T009)
- T021-T025: Testing and validation (sequential manual work)

**Phase 6 (Polish)**:
- T026, T027, T029, T030, T031: Can run in parallel [P]
- T028: Can run after any story (not marked [P] as single task)

---

## Parallel Example: Phase 2 (Foundational)

**Execute 5 tasks in parallel** (different files, no dependencies):

```bash
Task T004: Create storageManager.ts
Task T005: Create contentParser.ts
Task T006: Create translationApi.ts
Task T007: Create types.ts
Task T008: Swizzle DocSidebar

# All 5 tasks complete in parallel, then Phase 3 can begin
```

---

## Parallel Example: Phase 3 (User Story 1)

**Execute 3 tasks in parallel** (component + styles + export):

```bash
Task T009: Create TranslationButton.tsx
Task T010: Create TranslationButton.module.css
Task T011: Create index.ts

# All 3 tasks complete in parallel

# Then sequential:
Task T012: Integrate into DocSidebar (depends on T009, T008)
Task T013: Manual testing (depends on T012)
Task T014: Error handling tests (depends on T012)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only) - Recommended for Hackathon

1. **Complete Phase 1** (Setup): 15 minutes
2. **Complete Phase 2** (Foundational): 45 minutes (parallel: 20 minutes)
3. **Complete Phase 3** (User Story 1): 90 minutes (parallel: 45 minutes)
4. **STOP and VALIDATE**: Manual testing of translation and toggle
5. **Deploy/Demo**: Working MVP with "Translate to Urdu" button ✅

**Total time (with parallelization): ~2 hours**

### Incremental Delivery (Full Feature)

1. **Setup + Foundational**: Foundation ready (30 minutes)
2. **Add User Story 1**: Test independently, deploy MVP (1-2 hours)
3. **Add User Story 2**: Add persistence, test independently (1-2 hours)
4. **Add User Story 3**: Validate quality, finalize (1-2 hours)
5. **Polish & deploy**: Final refinements (1 hour)

**Total time: 5-8 hours**

### Parallel Team Strategy (3 Developers)

1. **Team together**: Complete Setup + Foundational (45 minutes)
2. **After Foundational**:
   - Developer A: User Story 1 (1-2 hours) → Deploy MVP
   - Developer B: User Story 2 (1-2 hours) → Test with US1
   - Developer C: User Story 3 QA (1-2 hours) → Validate quality
3. **Merge**: All stories complete independently and integrate seamlessly

**Total elapsed time: 2-3 hours (parallel)**

---

## Success Criteria per Story

### User Story 1: Translation Works
- ✅ Button visible on all chapters (Modules 1-4)
- ✅ Translation completes in <3 seconds (SC-002)
- ✅ Content shows in Urdu after translation
- ✅ Button click toggles to/from English
- ✅ Code blocks unchanged (FR-009)
- ✅ Formatting preserved (headings, lists, links)
- ✅ Errors handled gracefully with retry option

### User Story 2: Preference Persists
- ✅ Preference saved to localStorage on toggle
- ✅ Auto-translation on page load if preference is Urdu
- ✅ Preference persists across chapter navigation
- ✅ Preference persists across browser reload
- ✅ Works even if localStorage unavailable (degrades gracefully)

### User Story 3: Quality Validated
- ✅ Translation accuracy ≥95% (SC-003, manual review)
- ✅ Code blocks remain unchanged
- ✅ Technical terms translated correctly
- ✅ Urdu renders correctly in all browsers
- ✅ Educational tone maintained
- ✅ Special characters and unicode work correctly

---

## Notes & Guidelines

- **Parallel marked [P]**: Can execute simultaneously (different files, no blocking dependencies)
- **Story labels [US1] [US2] [US3]**: Trace tasks to specific user stories for impact analysis
- **Each user story independently testable**: Can stop at any checkpoint and validate story alone
- **Avoid cross-story dependencies**: Stories should be independently deployable
- **Manual testing critical**: Translation quality requires human review
- **Performance targets**: <3 seconds translation, <100ms button interaction
- **Error handling priority**: Graceful fallbacks for all failure scenarios
- **Commit after each task**: Frequent, small commits enable easy rollback

---

## Rollback Strategy

If issues occur:
- **Phase 3 (US1) broken**: Disable button in DocSidebar temporarily, rollback T012
- **Phase 4 (US2) broken**: Keep translations working, disable auto-apply, rollback T016
- **Phase 5 (US3) quality issues**: Keep feature working, improve prompt, re-test
- **API key/quota issues**: Document in TESTING.md, provide fallback key for development

---

**Ready to implement! 🚀**

Start with Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1) for MVP
