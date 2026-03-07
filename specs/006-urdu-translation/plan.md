# Implementation Plan: Urdu Translation Feature

**Branch**: `006-urdu-translation` | **Date**: 2026-02-01 | **Spec**: [specs/006-urdu-translation/spec.md](spec.md)
**Input**: React translation component integrated into Docusaurus theme, OpenAI GPT-4 API for real-time translation, localStorage for preference persistence, MDX content parsing with code block preservation.

## Summary

Add a "Translate to Urdu 🌐" button to each chapter in Modules 1-4 of the Front-End Book (Docusaurus-based). Clicking translates visible chapter prose to Urdu via OpenAI GPT-4 API while preserving code blocks, formatting, and links. User preference persists in localStorage across sessions. The feature integrates as a reusable React component in Docusaurus theme customization.

---

## Technical Context

**Language/Version**: TypeScript/JavaScript (React 19.x, Node 20+) with Python 3.10+ backend API
**Primary Dependencies**:
- Frontend: React 19, @docusaurus/core 3.9.2, openai (JS SDK)
- Optional backend helper: FastAPI + Python to wrap OpenAI calls (for API key security)

**Storage**: Browser localStorage for preference, optional Redis/Postgres for server-side translation cache (deferred)
**Testing**: Jest/React Testing Library (frontend), pytest (backend if included)
**Target Platform**: Web (Docusaurus static site + client-side React)
**Project Type**: Web application (frontend-primary)
**Performance Goals**:
- Translation API call completes in < 3 seconds (SC-002)
- Button interaction <100ms perceived latency
- localStorage read/write <50ms

**Constraints**:
- Code blocks MUST NOT be translated (FR-009)
- OpenAI API quota/cost management required
- localStorage ~5-10MB limit per domain
- No external web search or hallucination (constitution principle: RAG grounding)

**Scale/Scope**:
- Modules 1-4 (~30-50 chapters per module, ~2000 chars average prose per chapter)
- Estimated 10,000-20,000 API calls/month in pilot phase
- Single language pair (English → Urdu only, P1 scope)

---

## Constitution Check

**Reference**: Constitution Principles I-V from `.specify/memory/constitution.md`

### ✅ Principle I: Technical Accuracy and Sourcing
- **Status**: PASS with mitigation
- **Check**: Translation uses OpenAI GPT-4 (documented, state-of-the-art for multilingual NMT)
- **Requirement**: Code examples remain unchanged; translations validated against Urdu language expert review in QA
- **Mitigation**: Add acceptance test: "Translated chapter matches 95% of human-reviewed baseline translation"

### ✅ Principle II: Hands-On Learning Through Working Code
- **Status**: PASS
- **Check**: Translation feature requires no new code examples; it's a UX enhancement to existing chapters
- **Impact**: Does not change pedagogical value of working code examples

### ✅ Principle III: Spec-Driven Development and Full Documentation
- **Status**: PASS
- **Check**: This feature follows complete spec → plan → tasks → implementation pipeline
- **Constraint**: All responses from translation use official content only (no external hallucination); aligned with RAG grounding principle

### ✅ Principle IV: Modular, Progressive Content Architecture
- **Status**: PASS
- **Check**: Translation applies uniformly to all modules 1-4; does not alter module sequencing or prerequisites
- **Design**: Toggle is transparent to learning flow; learner chooses language preference

### ✅ Principle V: Safety, Simulation-First, and Hardware Flexibility
- **Status**: PASS
- **Check**: Feature is client-side and read-only (no safety impact on robotics hardware/simulation code)
- **Design**: No code generation, no robot control, no hardware access

### 🟢 Gate Result: **PASS** — No constitution violations. Feature aligns with all principles.

---

## Project Structure

### Documentation (this feature)

```text
specs/006-urdu-translation/
├── spec.md                           # Feature specification ✓
├── plan.md                           # This file ✓
├── research.md                       # Phase 0: Research findings (to be created)
├── data-model.md                     # Phase 1: Data model (to be created)
├── contracts/                        # Phase 1: API contracts (to be created)
│   ├── openai-translation-api.md
│   └── frontend-api.md
├── quickstart.md                     # Phase 1: Setup guide (to be created)
├── checklists/
│   └── requirements.md               # Quality validation ✓
└── tasks.md                          # Phase 2: Actionable tasks (to be created by /sp.tasks)
```

### Source Code (Frontend)

```text
Front-End-Book/src/
├── components/
│   └── TranslationButton/            # NEW: Translation component
│       ├── TranslationButton.tsx      # Button UI + translation logic
│       ├── TranslationButton.module.css
│       ├── types.ts                  # TranslationState, TranslationPreference
│       └── __tests__/
│           └── TranslationButton.test.tsx
│
├── utils/
│   ├── translationApi.ts             # NEW: OpenAI API wrapper
│   ├── contentParser.ts              # NEW: MDX/HTML content parsing
│   └── storageManager.ts             # NEW: localStorage + fallback handling
│
├── context/
│   └── TranslationContext.ts         # NEW: Global translation state (optional)
│
└── theme/
    └── DocSidebar.tsx                # MODIFY: Inject TranslationButton into chapter header
```

### Source Code (Optional Backend)

```text
backend/
├── app/
│   ├── main.py                       # NEW: FastAPI app
│   ├── models.py                     # Translation request/response models
│   ├── services/
│   │   └── translation_service.py    # Wrapper around OpenAI client
│   └── routes/
│       └── translate.py              # POST /api/translate endpoint
├── requirements.txt                  # Add: openai, fastapi, pydantic
└── tests/
    └── test_translation.py
```

**Structure Decision**:

This is a **web application (frontend-primary)** with optional backend component.

**Primary Path** (Recommended for MVP): Client-side only
- Translate component calls OpenAI JS SDK directly from browser
- API key stored in environment variable (Docusaurus build-time)
- Simple, fast, no backend infrastructure needed
- **Trade-off**: API key exposed in frontend (mitigated by rate limiting in OpenAI account)

**Alternative Path** (Recommended for production): Client + lightweight backend
- Backend FastAPI server wraps OpenAI calls
- Frontend calls `POST /api/translate` instead of OpenAI directly
- Better security (API key hidden on server), enables caching, usage tracking
- **Trade-off**: Additional backend deployment required

**Decision for MVP**: Use **Primary Path (client-side)** to launch quickly. Migration to backend can happen in Phase 2 if needed.

---

## Complexity Tracking

| Consideration | Resolution |
|---------------|-----------|
| **API Key Exposure** | Client-side approach uses environment variable accessible at build time. For production, switch to backend proxy (Phase 2). MVP acceptable given Hackathon timeline. |
| **Rate Limiting** | Rely on OpenAI account-level rate limits initially; implement client-side debouncing and caching (Phase 2). |
| **Content Parsing** | Docusaurus renders MDX as HTML at runtime. Parse rendered HTML via DOM API to identify translatable text nodes and code blocks. Safer than parsing markdown. |
| **Urdu Unicode Rendering** | React/browser handle Urdu natively; test across Chrome, Firefox, Safari to verify rendering. No special font embedding needed. |

---

## Phase 0: Research (To Be Created)

Will resolve:
- ✅ OpenAI GPT-4 API integration: authentication, quota, cost modeling, response format
- ✅ Docusaurus theme customization: swizzling vs. wrapping, where to inject button
- ✅ MDX/HTML content parsing: identifying translatable vs. code block sections
- ✅ localStorage best practices: error handling when disabled, quota management
- ✅ Urdu translation validation: accuracy testing, technical term handling

---

## Phase 1: Design & Contracts (To Be Created)

Will produce:
- **data-model.md**:
  - TranslationPreference (language: 'en' | 'ur', savedAt: timestamp)
  - ChapterContent (title, sections[], codeBlocks[])
  - TranslationState (isLoading, error, translatedText, language)

- **contracts/**:
  - OpenAI API request/response (already documented by OpenAI SDK)
  - Frontend internal API: `translate(content: string, targetLanguage: 'ur'): Promise<string>`

- **quickstart.md**:
  - Setup development environment (Node 20+, npm install)
  - Run Docusaurus locally (`npm start`)
  - Configure OpenAI API key in environment
  - Manual test: click button, verify translation renders
  - Run unit tests

---

## Phase 1: Agent Context Update

Will run:
```bash
.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```

This will add to agent context:
- React + TypeScript best practices for Docusaurus
- OpenAI JS SDK integration patterns
- localStorage error handling and testing

---

## Gates and Readiness

### Phase 0 Entry Gate: ✅ PASS
- Specification complete with all requirements testable ✓
- Constitution check passed ✓
- Technical context identified (no blocking unknowns) ✓
- Ready to research OpenAI integration and Docusaurus customization patterns

### Phase 1 Entry Gate: (Pending Phase 0 completion)
- All NEEDS CLARIFICATION from research.md resolved ✓
- Design decisions documented ✓
- Ready to code and test

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| OpenAI API quota exceeded | Medium | API calls fail, feature unavailable | Implement client-side request debouncing; monitor usage in QA |
| Urdu text rendering issues | Low | Garbled output in some browsers | Test across Chrome/Firefox/Safari with native Urdu fonts |
| localStorage disabled | Low | Preference not saved | Graceful fallback: translate works, preference resets per session |
| Code block included in translation | Medium | Corrupted code examples | Parse HTML DOM to identify `<code>` blocks; exclude from prompt |
| API key exposed in frontend | Medium | Key revoked, rate-limited | Short-term: use environment variable + rate limiting. Phase 2: move to backend. |

---

## Success Metrics (from Spec)

- **SC-001**: Translation button visible at top of every chapter ← Integration test
- **SC-002**: Translation completes in <3 seconds ← Performance benchmark
- **SC-003**: 95% of content translated accurately ← Manual review + accuracy test
- **SC-004**: Preference persists across browser sessions ← localStorage test
- **SC-005**: Code blocks preserved ← HTML parsing test
- **SC-006**: Errors handled gracefully ← Error handling test

---

## Appendix: Technology Stack Justification

| Technology | Why Selected | Alternatives Considered |
|------------|-------------|------------------------|
| **React 19** | Already used in Front-End Book; Docusaurus native; familiarity | Vue, vanilla JS (overkill) |
| **TypeScript** | Type safety for API integration; prevents runtime errors | JavaScript (less safe) |
| **OpenAI GPT-4** | Spec requirement; state-of-the-art multilingual translation; low cost | Google Translate API (less accurate for technical), Hugging Face (self-hosted, higher latency) |
| **localStorage** | Spec requirement; simple, no backend needed for MVP | IndexedDB (overkill), cookies (limited size) |
| **Docusaurus theme swizzling** | Native support; clean integration; no fork needed | Custom plugin (more complex) |

---

## Next Steps

1. ✅ Specification complete and validated
2. ✅ Plan document complete
3. ➡️ **Next**: Run `Phase 0 research` (resolve all unknowns)
4. ➡️ **Then**: Run `Phase 1 design` (create data model, contracts, quickstart)
5. ➡️ **Finally**: Run `/sp.tasks` to generate actionable implementation tasks
