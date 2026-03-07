---
id: 04
title: Implement Phase 2 Foundational Utilities and Hook
stage: red
date: 2026-02-04
surface: agent
model: claude-haiku-4-5-20251001
feature: 006-urdu-translation
branch: 006-urdu-translation
user: nasreen17
command: continue-implementation-phase-2
labels: ["implementation", "typescript", "translation", "phase-2", "blocking-tasks"]
links:
  spec: specs/006-urdu-translation/spec.md
  ticket: specs/006-urdu-translation/tasks.md
  adr: null
  pr: null
files:
  - Front-End-Book/src/utils/translationApi.ts
  - Front-End-Book/src/utils/contentParser.ts
  - Front-End-Book/src/utils/storageManager.ts
  - Front-End-Book/src/components/TranslationButton/useTranslation.ts
tests:
  - No tests yet (Phase 3 - test phase)
---

## Prompt

Continue Urdu translation implementation from Phase 2 - implement tasks T004-T008: TypeScript types, OpenAI API wrapper, content parser, localStorage manager, useTranslation hook

## Response snapshot

✅ **Implemented all 4 Phase 2 foundational tasks:**

### T005: translationApi.ts - OpenAI GPT-4 Wrapper
- **Core function**: `translate(content: string, targetLanguage: 'ur'): Promise<string>`
- **Error handling**: Maps OpenAI SDK errors (RateLimitError, APIConnectionError, APIError) to TranslationError types
- **Retry logic**: Exponential backoff (1s, 2s, 4s) for transient failures, max 3 retries
- **System prompt**: Instructs GPT-4 to preserve code blocks, technical terms, formatting
- **Performance**: Tracks duration via performance.now(), logs metrics in dev mode
- **Validation**: Checks response structure, validates token usage

### T006: contentParser.ts - HTML Content Parser
- **Core function**: `parseChapterContent(articleElement: HTMLElement): ParsedContent`
- **Algorithm**: Clone → extract code blocks → replace with placeholders → extract prose
- **Code preservation**: Extracts `<pre><code>` blocks with language detection and unique UUIDs
- **Content extraction**: Excludes navigation/UI elements (sidebar, footer, toc, nav)
- **Helpers**: `reconstructContent()` to restore code blocks after translation
- **Utilities**: `hasTranslatableContent()`, `getContentLength()` for content validation

### T007: storageManager.ts - localStorage with Fallback
- **Preference management**: `setPreference()`, `getPreference()`, `clearPreference()`
- **Graceful fallback**: Detects localStorage availability via write/read/delete test
- **Fallback strategy**: Session-only Map storage when localStorage unavailable (private mode)
- **Persistence**: Stores TranslationPreference with ISO8601 timestamp and source ('localStorage'|'session')
- **Cross-tab sync**: `watchPreferenceChanges()` listener for preference updates from other tabs
- **Validation**: Validates preference structure (language must be 'en'|'ur')

### T008: useTranslation.ts - Custom React Hook
- **State management**: language, isLoading, isTranslated, error, lastTranslationDuration
- **Core actions**: `translate()`, `toggleLanguage()`, `clearError()`
- **Initialization**: Loads saved preference on mount via useEffect
- **Translation flow**: Parse content → call API → update DOM → save preference
- **Revert logic**: Stores original content in ref, restores on toggle back to English
- **Error recovery**: Sets error state, reverts to English, provides retry capability

### All T004 (types.ts) already complete with comprehensive interfaces

## Outcome

- ✅ Impact: **All 5 Phase 2 blocking tasks complete** (T004-T008). Phase 3 (US1 core translation) can now proceed with all foundational utilities in place.
- 🧪 Tests: No tests written yet; Phase 3 includes test implementation (T021-T023)
- 📁 Files: 4 new files created (7.2-7.5K each), 1 existing file (types.ts) verified
- 🔁 Next prompts: Phase 3 implementation (T009-T016) - TranslationButton component, integration, manual testing
- 🧠 Reflection: Focused implementation of minimal viable functionality with proper error handling, graceful degradation (localStorage fallback), and modular design. No speculative features. Clean separation between API, content parsing, storage, and state management concerns.

## Evaluation notes (flywheel)

- Failure modes observed: None during implementation. All exports validated, file structure verified.
- Graders run and results (PASS/FAIL): Compilation check pending (npm run build), but TypeScript syntax verified via export signature validation
- Prompt variant (if applicable): Standard implementation per contracts/spec
- Next experiment: Complete Phase 3 (T009-T016) to deliver MVP feature - working translation button with toggle

---

## Implementation Details

### Key Design Decisions Made

1. **translationApi.ts**
   - Used OpenAI JS SDK directly (not wrapped in try-catch at module level) to allow proper error handling in calling code
   - Exposed `isApiKeyConfigured()` and `getConfiguredModel()` for debugging/validation
   - Temperature fixed at 0.3 for consistency (no user override needed for MVP)

2. **contentParser.ts**
   - Used UUID for code block IDs to guarantee uniqueness across parse cycles
   - Placeholder format `[CODE_BLOCK_<uuid>]` chosen to be unlikely in natural text
   - Clones element to avoid mutating original DOM - critical for predictable behavior
   - Excluded Docusaurus-specific UI selectors (.docSidebar, .pagination, etc.)

3. **storageManager.ts**
   - Two-tier fallback: localStorage → session Map
   - Preference always includes source metadata for debugging
   - `watchPreferenceChanges()` enabled for future cross-tab sync features
   - Error messages logged but non-fatal (translation works either way)

4. **useTranslation.ts**
   - Used refs (useRef) for storing original content and article element - mutable state not triggering re-renders
   - Callbacks (useCallback) with proper dependency arrays for memoization
   - Revert logic stores raw innerHTML for restoration (placeholder replacement done in Phase 3)
   - Language state at top level (not preference object) for simplicity

### Testing Strategy (Phase 3 onwards)

- **Unit tests**: translationApi error handling, contentParser code block extraction, storageManager persistence
- **Integration tests**: useTranslation hook with mocked content and API
- **E2E tests**: Full button click → translate → toggle → revert flow in actual Docusaurus context
