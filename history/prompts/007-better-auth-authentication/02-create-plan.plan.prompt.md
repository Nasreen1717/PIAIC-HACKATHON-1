---
ID: 002
TITLE: Create Better-Auth Implementation Plan
STAGE: plan
DATE_ISO: 2026-02-07
SURFACE: agent
MODEL: claude-haiku-4-5-20251001
FEATURE: better-auth-authentication
BRANCH: 007-better-auth-authentication
USER: nasreen17
COMMAND: /sp.plan
LABELS:
  - implementation-plan
  - architecture
  - backend
  - frontend
  - full-stack
LINKS:
  SPEC: specs/007-better-auth-authentication/spec.md
  PLAN: specs/007-better-auth-authentication/plan.md
  TICKET: null
  ADR: null
  PR: null
FILES_YAML:
  - specs/007-better-auth-authentication/plan.md
TESTS_YAML:
  - null
---

# Prompt History Record: Create Better-Auth Implementation Plan

## PROMPT_TEXT

```
/sp.plan

Create implementation plan for Better-Auth integration with:

1. ADRs (Architecture Decision Records):
   - JWT storage (localStorage vs httpOnly cookies)
   - State management (Context vs Redux)
   - Form library (react-hook-form vs Formik)
   - Backend auth (python-jose vs fastapi-users)

2. Tech Stack:
   Frontend: better-auth, react-hook-form, zod, React Context
   Backend: python-jose, passlib[bcrypt], SQLAlchemy

3. File Structure (what to create/modify):
   New: SignupPage, SigninPage, AuthProvider, ProtectedRoute, UserMenu, auth.py, security.py, user.py
   Modify: TranslationButton.tsx, main routes

4. Implementation Phases (priority order)
5. Testing Strategy (unit, integration, e2e)
6. Deployment Steps
7. Timeline: 5-8 hours breakdown

Decisions made: Unlimited sessions, password reset out of scope. Focus on MVP for hackathon deadline.
```

## RESPONSE_TEXT

Comprehensive implementation plan created for Better-Auth Authentication System with:

**Architecture Decisions (4 ADRs)**:
1. JWT Storage: localStorage + HttpOnly cookie fallback
2. State Management: React Context API (no Redux needed)
3. Form Validation: react-hook-form + zod (lightweight, type-safe)
4. Backend Auth: python-jose + passlib[bcrypt] (direct implementation, not fastapi-users - simpler for MVP)

**Tech Stack Confirmed**:
- Frontend: React 19 + TypeScript, react-hook-form, zod, axios, React Context
- Backend: FastAPI, python-jose (JWT), passlib[bcrypt] (password hashing), SQLAlchemy ORM
- Database: Existing Neon Postgres (new tables: users, user_backgrounds)

**File Structure**:
- **Frontend**: 7 new components (SignupPage, SigninPage, AuthProvider, ProtectedRoute, UserMenu, ProfilePage) + 3 hooks (useAuth, authApi, modified axios)
- **Backend**: 3 new modules (security.py, user.py models, auth.py routes) + modified main.py for CORS
- **Database**: 2 new tables (users with password_hash, user_backgrounds with questionnaire fields)

**Implementation Phases** (5-8 hours):
1. Backend Foundation (2h): Models, security functions, auth endpoints
2. Frontend Components (2h): All UI components with react-hook-form validation
3. Integration (1h): AuthProvider in Root, protected features, route setup
4. Polish & Testing (1-2h): Error handling, token expiry, unit/integration tests

**Testing Strategy**:
- Backend: 14 unit tests (hashing, token creation), 10 integration tests (endpoints)
- Frontend: 3 component test files (Signup, Signin, ProtectedRoute), 8+ test cases per component
- E2E: Manual test flow (signup → signin → use features → signout)

**Deployment**:
- Backend: Add env vars (JWT_SECRET, DATABASE_URL, CORS_ORIGINS), run migrations, start uvicorn
- Frontend: Install deps, build, configure API endpoint, npm run start

**Timeline Breakdown**: Setup (30min) → Phase 1 (2.5h) → Phase 2 (1.5h) → Phase 3 (1h) → Phase 4 (1-2h) = 5-8 hours total

**Constitution Check**: ✅ PASS - Follows spec-driven development, no over-engineering, security by default, incremental delivery

**Status**: Plan finalized and ready for `/sp.tasks` to generate actionable development tasks.

## DECISIONS_MADE

1. **JWT Token Storage**: localStorage for MVP (simpler development), with HttpOnly cookie support for production
2. **State Management**: React Context (simpler than Redux, sufficient for auth-only state)
3. **Form Library**: react-hook-form + zod (lightweight, type-safe, minimal dependencies)
4. **Backend Auth**: python-jose + passlib[bcrypt] directly (not fastapi-users - simpler, more control, fewer dependencies for MVP)
5. **Concurrent Sessions**: Unlimited (users can sign in on multiple devices)
6. **Password Reset**: Out of scope for MVP (admin reset only, future enhancement)

## ARCHITECTURE_DECISIONS

- **ADR-001**: JWT Storage Strategy → localStorage + HttpOnly cookie fallback
- **ADR-002**: Frontend State Management → React Context API (no Redux)
- **ADR-003**: Form Library & Validation → react-hook-form + zod
- **ADR-004**: Backend Authentication Library → python-jose + passlib[bcrypt]

## TECHNICAL_CONTEXT

**Frontend**: TypeScript/React 19 with Docusaurus 3.9.2
**Backend**: Python 3.11+ with FastAPI
**Storage**: Neon Postgres (existing connection)
**Performance Goals**: Signup/signin <2s, token validation <100ms
**Constraints**: No breaking changes to chatbot, CORS for localhost:3000 + localhost:8080, mobile responsive, zero console errors

## DATA_MODEL

**User Table**: id, email (unique), password_hash, full_name, created_at, updated_at
**UserBackground Table**: id, user_id (FK), software_background, hardware_background, ros_experience, python_level, learning_goal, available_hardware

**5 API Endpoints**:
1. POST /api/auth/signup → returns JWT token + user info
2. POST /api/auth/signin → returns JWT token (7-day or 30-day with remember_me)
3. GET /api/users/me → returns user profile (requires JWT)
4. PUT /api/users/{id} → updates profile (requires JWT)
5. POST /api/auth/signout → logs out user (requires JWT)

## PROJECT_STRUCTURE

**Frontend Components** (7 new + 2 modified):
- SignupPage, SigninPage, AuthProvider, ProtectedRoute, UserMenu, ProfilePage (new)
- useAuth hook, authApi service (new)
- TranslationButton, PersonalizationButton (modified to check auth)

**Backend Modules** (3 new + 2 modified):
- security.py (Bcrypt + JWT utilities)
- user.py (User + UserBackground models)
- auth.py routes (5 endpoints)
- main.py (modified for CORS)
- requirements.txt (add dependencies)

## TESTING_STRATEGY

**Backend**: 24 tests (14 unit + 10 integration) covering password hashing, JWT creation/verification, endpoint auth
**Frontend**: 20+ test cases covering signup validation, signin flow, protected route, useAuth hook
**E2E**: Manual test of complete auth flow (signup → signin → protected features → signout)
**Quality Checks**: Zero console errors, mobile responsive (320px+), no chatbot regressions

## NEXT_STEPS

1. Generate detailed tasks with `/sp.tasks` for actionable development items
2. Begin Phase 1: Backend foundation (models + security.py + auth endpoints)
3. Target: 50 hackathon bonus points, 5-8 hours implementation
4. Ship MVP: auth flow + feature protection + profile management

## VALIDATION_RESULTS

✅ **Plan Quality Checklist**:
- ✅ Clear architecture decisions (4 ADRs documented)
- ✅ Complete tech stack specified (frontend, backend, database)
- ✅ File structure detailed (what to create/modify/delete)
- ✅ Phases prioritized (backend first, integration last)
- ✅ Testing strategy comprehensive (unit, integration, e2e)
- ✅ Deployment steps documented (env setup, migrations, start commands)
- ✅ Timeline realistic (5-8 hours with breakdown)
- ✅ Risks identified with mitigations
- ✅ Constitution check passing (spec-driven, no over-engineering)

**Plan Status**: COMPLETE and ready for implementation phase
