---
id: 02
title: Urdu Translation Implementation Plan
stage: plan
date: 2026-02-04
surface: agent
model: claude-haiku-4-5-20251001
feature: 006-urdu-translation
branch: 006-urdu-translation
user: user
command: /sp.plan
labels: ["planning","architecture","react","openai","docusaurus","internationalization"]
links:
  spec: /specs/006-urdu-translation/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-urdu-translation/plan.md
  - specs/006-urdu-translation/research.md
  - specs/006-urdu-translation/data-model.md
  - specs/006-urdu-translation/contracts/frontend-api.md
  - specs/006-urdu-translation/contracts/openai-api.md
  - specs/006-urdu-translation/quickstart.md
tests:
  - Constitution alignment check: PASS (5/5 principles)
  - Architecture review: PASS
  - Data model validation: PASS
  - API contracts generated: PASS
---

## Prompt

```
Urdu translation architecture: React button component structure, OpenAI GPT-4 API integration, localStorage persistence strategy, Docusaurus theme swizzling approach, content chunking for long chapters, formatting preservation logic
```

## Response snapshot

**Complete implementation plan generated for Urdu Translation Feature addressing all architectural concerns:**

### Phase 0: Research (✅ Complete)

**Resolved**:
- ✅ OpenAI GPT-4 API integration: Client-side JS SDK (MVP), backend proxy (Phase 2)
- ✅ Docusaurus theme customization: Theme swizzling approach validated
- ✅ MDX/HTML content parsing: DOM-based parsing strategy for code block preservation
- ✅ localStorage best practices: Error handling, fallback to session-only
- ✅ Urdu translation validation: Technical term handling, accuracy testing approach

**Key Findings** (`research.md`):
- OpenAI JS SDK integration documented with cost model (~$60-120/month for pilot)
- Docusaurus swizzling approach identified (clean, no fork needed)
- Content parsing strategy: Extract HTML from DOM, identify `<code>` blocks, exclude from translation
- localStorage fallback when disabled: In-session translation works, preference resets per session
- Temperature setting: 0.3 for consistency, max_tokens: 4000 for chapter-length content

### Phase 1: Design (✅ Complete)

**Data Model** (`data-model.md`):
- **TranslationPreference**: Language preference ('en'|'ur'), timestamp, storage source
- **ChapterContent**: Sections, code blocks, metadata with module/chapter identification
- **TranslationState**: Loading, error, translated text, language flag
- **State Lifecycle**: Load preference → User toggles → Update → Save → Re-render

**API Contracts** (`contracts/`):
- `openai-api.md`: GPT-4 request/response format, system prompt for preservation
- `frontend-api.md`: Internal `translate(content, targetLanguage)` interface, error handling

**Quickstart** (`quickstart.md`):
- Development setup: Node 20+, OpenAI API key configuration
- Manual testing procedure: Click button, verify translation, check code preservation
- Unit test patterns for translation logic, localStorage, UI components

### Architecture Decisions

1. **MVP Path (Recommended)**: Client-side only
   - Direct OpenAI JS SDK calls from browser
   - API key in environment variable (Docusaurus build-time)
   - Simple, fast deployment
   - Trade-off: API key exposure (mitigated by rate limiting)

2. **Production Path (Phase 2)**: Client + Backend
   - FastAPI backend wraps OpenAI calls
   - API key hidden on server
   - Enables caching and usage tracking
   - Trade-off: Additional deployment infrastructure

3. **Theme Integration**: Docusaurus swizzling (not fork)
   - Wrap DocSidebar component
   - Inject button in article header
   - Clean, maintainable, no core fork

4. **Content Parsing**: DOM-based (not markdown)
   - Docusaurus renders MDX as HTML at runtime
   - Parse rendered HTML to identify translatable vs code sections
   - Safer than markdown parsing; respects Docusaurus transformations

5. **Code Block Preservation**: HTML-based exclusion
   - Identify `<code>`, `<pre>` tags in DOM
   - Exclude from translation prompt
   - Preserve original code examples

### Constitution Alignment (✅ PASS)

- **Principle I** (Technical Accuracy): GPT-4 + code preservation + expert validation ✅
- **Principle II** (Hands-On Learning): No new code examples, UX enhancement only ✅
- **Principle III** (SDD): Follows complete spec→plan→tasks pipeline ✅
- **Principle IV** (Modular Architecture): Uniform application, transparent to learning flow ✅
- **Principle V** (Safety/Hardware): Client-side, read-only, no robotics impact ✅

### Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| OpenAI API quota exceeded | Client-side debouncing (500ms), usage monitoring |
| Urdu rendering issues | Cross-browser testing (Chrome, Firefox, Safari) |
| localStorage disabled | Graceful fallback to session-only state |
| Code included in translation | DOM parsing to exclude `<code>` blocks |
| API key exposure | Environment variable + rate limiting (MVP), backend proxy (Phase 2) |

### Project Structure

```
specs/006-urdu-translation/
├── spec.md                    ✅ Complete
├── plan.md                    ✅ Complete
├── research.md                ✅ Complete
├── data-model.md              ✅ Complete
├── contracts/
│   ├── openai-api.md          ✅ Complete
│   └── frontend-api.md        ✅ Complete
├── quickstart.md              ✅ Complete
└── checklists/requirements.md ✅ Complete

Source Code (To Implement):
Front-End-Book/src/
├── components/TranslationButton/
│   ├── TranslationButton.tsx
│   ├── TranslationButton.module.css
│   ├── types.ts
│   └── __tests__/TranslationButton.test.tsx
├── utils/
│   ├── translationApi.ts
│   ├── contentParser.ts
│   └── storageManager.ts
└── theme/DocSidebar.tsx (MODIFY)
```

### Next Phase

✅ **Ready for `/sp.tasks`** - All architecture decisions documented, no blocking unknowns.

Generate actionable implementation tasks based on this plan covering:
- Component structure and lifecycle
- API integration and error handling
- localStorage persistence and fallback
- Content parsing and code block preservation
- Testing (unit, integration, E2E)
- Documentation and deployment

---

## Outcome

- ✅ Impact: Complete architecture plan ready for implementation
- 🧪 Tests: Constitution check PASSED (5/5 principles), architecture validation PASSED
- 📁 Files: 7 planning artifacts completed (plan.md, research.md, data-model.md, 2 contracts, quickstart.md, checklist)
- 🔁 Next prompts: `/sp.tasks` to generate implementation task list
- 🧠 Reflection: Plan is comprehensive with clear MVP vs production paths, documented trade-offs, and constitution alignment. No blocking unknowns remain.

## Evaluation notes (flywheel)

- Failure modes observed: None - all planning artifacts complete and coherent
- Graders run and results (PASS/FAIL): Constitution Check = PASS (5/5), Architecture Validation = PASS
- Prompt variant (if applicable): null
- Next experiment: Proceed to `/sp.tasks` for implementation task generation

