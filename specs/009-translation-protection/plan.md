# Implementation Plan: Translation Protection with Authentication

**Branch**: `009-translation-protection` | **Date**: 2026-02-10 | **Spec**: [Translation Protection with Authentication](./spec.md)
**Input**: Feature specification from `/specs/009-translation-protection/spec.md`

## Summary

Add authentication protection to the existing TranslationButton component in the Docusaurus-based Physical AI textbook. The feature restricts translation access to logged-in users only with clear UX messaging for logged-out users, while maintaining existing translation functionality. Backend API protection ensures unauthorized requests are rejected with HTTP 401.

**Technical Approach**: Leverage existing ProtectedFeature wrapper (already in place) on frontend; add JWT token validation middleware to backend `/api/translate` endpoint using existing FastAPI auth patterns from auth routes.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, python-jose (JWT), React, Docusaurus
**Storage**: Neon Serverless Postgres (existing user/auth data)
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Linux server (backend), web browser (frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Authentication check <50ms, translation API response <3s
**Constraints**: No breaking changes to existing translation flow, must work with hot reload
**Scale/Scope**: Single feature protecting one API endpoint, updating one component
**Endpoints Affected**: Backend creates new `/api/translate` endpoint or modifies existing one if present

## Constitution Check

**Gate: Must pass before Phase 0 research**

1. ✅ **Technical Accuracy & Sourcing** — Implementation uses existing FastAPI JWT patterns already documented in auth routes; no new external dependencies introduced
2. ✅ **Hands-On Learning** — Feature includes acceptance criteria with runnable tests (auth checks, token validation)
3. ✅ **Spec-Driven Development** — Complete spec, plan, and tasks (pending) follow the process
4. ✅ **Modular Progressive Content** — Feature is isolated, doesn't break existing modules
5. ✅ **Safety & Simulation-First** — No hardware concerns; security-focused (defense-in-depth with backend validation)

**Status**: ✅ PASS — No violations; proceeds to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/009-translation-protection/
├── spec.md                          # Feature requirements ✅
├── plan.md                          # This file (Phase 0-1 design)
├── research.md                      # Phase 0 output (unknowns resolved)
├── data-model.md                    # Phase 1 output (entities/state)
├── contracts/                       # Phase 1 output (API specs)
│   └── translate-api.openapi.json
├── quickstart.md                    # Phase 1 output (setup guide)
├── checklists/
│   └── requirements.md              # Quality validation ✅
└── tasks.md                         # Phase 2 output (actionable tasks)
```

### Source Code (repository root)

```text
# Frontend (Docusaurus, minimal changes)
Front-End-Book/
├── src/
│   ├── components/
│   │   ├── TranslationButton/
│   │   │   ├── index.tsx            # VERIFY auth usage already exists
│   │   │   ├── TranslationButton.module.css
│   │   │   ├── useTranslation.ts    # Hook for translation state
│   │   │   └── ErrorBoundary.tsx
│   │   └── Auth/
│   │       └── ProtectedFeature.tsx # Wrapper (already in place)
│   ├── context/
│   │   └── AuthContext.tsx          # User + token state
│   └── hooks/
│       └── useAuth.ts               # Hook to access AuthContext
└── tests/
    └── TranslationButton.test.tsx    # Frontend tests

# Backend (FastAPI)
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── chat.py              # Existing endpoint pattern
│   │       └── translate.py         # NEW: Translation endpoint (if missing)
│   ├── routes/
│   │   └── auth.py                  # Existing get_current_user dependency
│   ├── security.py                  # JWT utilities (already exists)
│   ├── main.py                      # Include translate router
│   └── schemas/
│       └── translate.py             # NEW: Request/response schemas
└── tests/
    ├── unit/
    │   └── test_translate_auth.py   # Unit test JWT validation
    └── integration/
        └── test_translate_flow.py   # E2E test auth + translation
```

**Structure Decision**: Web application (frontend + backend). Frontend is minimal wrapper around existing ProtectedFeature; backend adds single new router at `/api/translate` with JWT dependency from existing auth module.

## Complexity Tracking

No violations detected; no justification table needed.

---

## Phase 0: Outline & Research

### Identified Unknowns & Research Tasks

From the specification and context review, no significant unknowns remain:

1. ✅ **Frontend Auth Check Location**: Already decided by existing ProtectedFeature pattern — wraps content and checks `user` from useAuth
2. ✅ **Backend Middleware Pattern**: FastAPI Depends() pattern already established in auth routes (`get_current_user`)
3. ✅ **Error Response Format**: Existing auth routes return 401 with `{"detail": "..."}` pattern
4. ✅ **Token Storage**: localStorage with `auth_token` key (confirmed in AuthContext)
5. ✅ **JWT Validation**: python-jose already in use with `extract_email_from_token()` helper

### Research Consolidation

**Decision 1: Frontend Protection via ProtectedFeature**
- **Chosen**: Use existing ProtectedFeature wrapper (already applied in TranslationButton)
- **Rationale**: Component pattern already established; consistent with codebase; displays "Article translation requires authentication" message
- **Alternatives Considered**: Route guards (doesn't apply to component-level features), conditional rendering (subsumed by ProtectedFeature)
- **Verification**: Confirmed ProtectedFeature exists and is already wrapping TranslationButton in src/components/TranslationButton/index.tsx

**Decision 2: Backend Token Validation via get_current_user Dependency**
- **Chosen**: Reuse `get_current_user()` dependency from auth.py as FastAPI Depends()
- **Rationale**: Pattern already proven in auth routes; extracts JWT from Authorization header; validates token and fetches user
- **Alternatives Considered**: Custom middleware (overly complex), inline token checks (code duplication)
- **Implementation**: Import `get_current_user` into translate router; add it as parameter to endpoint

**Decision 3: Error Response Format**
- **Chosen**: HTTP 401 Unauthorized with detail message: `{"detail": "Not authenticated"}` or `{"detail": "Invalid or expired token"}`
- **Rationale**: Matches existing auth endpoint pattern; clear to frontend; no sensitive token information leaked
- **Alternatives Considered**: Custom error objects (unnecessary complexity)

**Decision 4: Translation Endpoint Location**
- **Chosen**: Create new `/api/v1/translate` router in `app/api/v1/translate.py` (if not already present)
- **Rationale**: Follows existing API structure; v1 versioning scheme; chat.py pattern reusable
- **Alternatives Considered**: Add to chat.py (mixing concerns), place in routes/ (inconsistent with v1 structure)

**Research Output**: No NEEDS CLARIFICATION items remain. All decisions grounded in existing codebase patterns.

---

## Phase 1: Design & Contracts

### 1. Data Model (entities & state)

**File**: `specs/009-translation-protection/data-model.md`

#### Entities

1. **User** (from existing AuthContext)
   - Fields: `id`, `email`, `full_name`, `is_active`, `created_at`
   - State: `token` (JWT), available via `useAuth()` hook
   - Validation: Non-null email, active status required

2. **TranslationRequest** (API payload)
   - Fields: `text` (content to translate), `source_lang` (default: "en"), `target_lang` (default: "ur")
   - Authentication: Requires valid JWT in Authorization header
   - Validation: Text non-empty, ≤50,000 chars

3. **TranslationResponse** (API response)
   - Fields: `translated_text` (result), `detected_lang` (auto-detected source), `confidence` (0.0-1.0)
   - Status: HTTP 200 on success, 401 on auth failure, 400 on invalid input, 503 on service error

4. **AuthenticationSession** (front-end state)
   - Stored in localStorage: `auth_token`, `auth_user`
   - Synced across tabs via storage events (FR-011)
   - Can expire; detected on API 401 response

### 2. API Contracts

**File**: `specs/009-translation-protection/contracts/translate-api.openapi.json`

```yaml
openapi: "3.0.0"
info:
  title: "Translation API"
  version: "1.0.0"
paths:
  /api/v1/translate:
    post:
      summary: "Translate text to target language"
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                text:
                  type: string
                  description: "Content to translate (≤50k chars)"
                source_lang:
                  type: string
                  default: "en"
                target_lang:
                  type: string
                  default: "ur"
      responses:
        "200":
          description: "Translation successful"
          content:
            application/json:
              schema:
                type: object
                properties:
                  translated_text: string
                  detected_lang: string
                  confidence: number
        "400":
          description: "Invalid input (empty text, too long)"
          content:
            application/json:
              schema:
                type: object
                properties:
                  detail: string
        "401":
          description: "Not authenticated (missing/invalid token)"
          content:
            application/json:
              schema:
                type: object
                properties:
                  detail: string
        "503":
          description: "Translation service unavailable"
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

### 3. Quick Start (integration guide)

**File**: `specs/009-translation-protection/quickstart.md`

#### Frontend Integration

1. Verify TranslationButton already wraps content in ProtectedFeature:
   ```tsx
   <ProtectedFeature featureName="Article translation">
     {/* translation button */}
   </ProtectedFeature>
   ```

2. Ensure useTranslation hook sends JWT token with API request:
   ```ts
   const response = await fetch('/api/v1/translate', {
     method: 'POST',
     headers: {
       'Authorization': `Bearer ${token}`,
       'Content-Type': 'application/json'
     },
     body: JSON.stringify({ text, target_lang: 'ur' })
   });
   ```

3. Handle 401 response by clearing auth state and showing login prompt

#### Backend Integration

1. Create `/api/v1/translate.py` with endpoint:
   ```python
   from fastapi import APIRouter, Depends
   from app.routes.auth import get_current_user, get_db

   @router.post("/translate")
   async def translate(
       request: TranslateRequest,
       current_user: User = Depends(get_current_user),
       db: AsyncSession = Depends(get_db)
   ):
       # Token validated by get_current_user dependency
       # Perform translation using existing service
       pass
   ```

2. Include router in main.py:
   ```python
   from app.api.v1 import translate
   app.include_router(translate.router)
   ```

### 4. Agent Context Update

**Action**: Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`

This will add the following to agent-specific context:
- FastAPI patterns for JWT validation
- ProtectedFeature component pattern
- Error handling patterns (401 responses)

---

## Phase 1 Artifacts Summary

| Artifact | Location | Purpose |
|----------|----------|---------|
| research.md | specs/009-translation-protection/research.md | Decisions & unknowns resolved |
| data-model.md | specs/009-translation-protection/data-model.md | Entity definitions & state management |
| translate-api.openapi.json | specs/009-translation-protection/contracts/ | API contract (OpenAPI) |
| quickstart.md | specs/009-translation-protection/quickstart.md | Integration guide for frontend & backend |

---

## Implementation Phases (High-Level)

### Phase 2: Tasks (Generated by `/sp.tasks`)

Will produce `tasks.md` with:
- T001: Verify existing TranslationButton uses ProtectedFeature ✅
- T002: Check if /api/translate endpoint exists (create if missing)
- T003: Add JWT dependency to translate endpoint
- T004: Test 401 responses for unauthorized requests
- T005: Test happy path (authenticated request succeeds)
- T006: Verify error handling on 401
- T007: Test token expiration scenarios
- T008: Mobile responsive testing
- T009: Integration test (full flow: logout → prompt → signin → translate)
- T010: Update frontend to handle 401 responses

### Phase 3: Implementation & Testing

Tasks executed by developer following tasks.md, delivering:
- ✅ Frontend protection (ProtectedFeature wrapper already in place)
- ✅ Backend JWT validation (get_current_user dependency)
- ✅ Error handling (401 responses)
- ✅ Tests (unit + integration + E2E)
- ✅ Mobile responsive validation

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Breaking existing translation | High | Test with authenticated users before commit; use feature flag if needed |
| Token not sent by frontend | High | Verify AuthContext provides token; check fetch config in useTranslation hook |
| CORS issues with Authorization header | Medium | Ensure backend CORS middleware allows "Authorization" in allowed_headers |
| Session expiry during translation | Medium | Frontend should detect 401 response, clear token, show login prompt |
| get_current_user dependency requires user in DB | Low | Token validation occurs before DB lookup; handle user not found gracefully |

---

## Success Metrics

- ✅ Logged-out users see authentication prompt (100%)
- ✅ Logged-in users can translate (100% of authenticated requests)
- ✅ Unauthorized API requests rejected (401 status)
- ✅ Zero console errors
- ✅ No performance degradation
- ✅ Mobile responsive (320px+)
- ✅ All acceptance scenarios pass

---

## Notes

1. **Frontend already protected**: TranslationButton already uses ProtectedFeature wrapper (confirmed in code review)
2. **Backend pattern established**: FastAPI get_current_user dependency proven in auth routes
3. **No new dependencies**: Uses existing JWT validation (python-jose), existing auth patterns
4. **Hot reload compatible**: Changes are isolated to API endpoint and component state
5. **Defense in depth**: Frontend check for UX; backend validation for security
6. **Testing strategy**: Unit tests for JWT validation; integration tests for full flow; E2E browser test

---

**Next Step**: Run `/sp.tasks` to generate `tasks.md` with granular implementation tasks.
