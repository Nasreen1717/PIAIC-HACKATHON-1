# Implementation Plan: Better-Auth Authentication System

**Branch**: `007-better-auth-authentication` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/007-better-auth-authentication/spec.md`

---

## Summary

Implement complete JWT-based authentication system for Physical AI textbook to protect translation and personalization features.

**Scope**:
- Frontend: Signup/Signin pages, AuthProvider (React Context), ProtectedRoute component, UserMenu with profile
- Backend: User model, authentication endpoints (signup/signin/signout/profile), JWT token management with Bcrypt password hashing
- Database: Users + UserBackground tables in existing Neon Postgres
- Security: HS256 JWT (7-day/30-day expiry), Bcrypt password hashing, CORS protection, request validation

**MVP Focus**: Complete auth flow (signup→signin→protected features) without email verification or password reset. Unlimited concurrent sessions. Auto-signin after signup. 5 frontend components + 5 backend endpoints targeting 50 hackathon bonus points in 4-6 hours.

---

## Technical Context

**Frontend Language/Version**: TypeScript/React 19.0.0 with Docusaurus 3.9.2
**Frontend Dependencies**: react-hook-form (form handling), zod (validation), axios (HTTP)
**Backend Language/Version**: Python 3.11+ with FastAPI
**Backend Dependencies**: python-jose (JWT), passlib[bcrypt] (password hashing), SQLAlchemy (ORM), pydantic (validation)
**Storage**: Neon Postgres (existing connection via environment variables)
**Testing**: pytest (backend unit/integration), React Testing Library (frontend)
**Target Platform**: Web (Docusaurus + FastAPI)
**Project Type**: Full-stack web application
**Performance Goals**: Signup/signin under 2 seconds, token validation under 100ms, profile updates instantaneous
**Constraints**:
- No breaking changes to existing RAG chatbot
- Use existing Neon Postgres connection
- CORS configured for localhost:3000 and localhost:8080
- No email verification or password reset in MVP
- Mobile responsive (320px+ viewports)
- Zero console errors

**Scale/Scope**:
- ~500 LOC backend (auth routes + models)
- ~800 LOC frontend (components + hooks)
- 10 new API endpoints (5 main + 5 helper/middleware)
- 1 new database table (Users) + 1 junction table (UserBackground)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-evaluate after Phase 1 design.*

**Project Principles** (from `.specify/memory/constitution.md`):

1. ✅ **Spec-Driven Development**: Feature spec completed before implementation
2. ✅ **User-Focused**: 5 user stories prioritized by value (P1: auth core, P2: profile/signout)
3. ✅ **Testable Acceptance Criteria**: All scenarios include Given/When/Then
4. ✅ **Technology-Agnostic Spec**: Spec describes WHAT not HOW
5. ✅ **Incremental Delivery**: MVP scope (no email/reset) allows 4-6 hour implementation
6. ✅ **No Over-Engineering**: 5 frontend components, 5 backend endpoints - minimal viable set
7. ✅ **Security by Default**: Bcrypt hashing, HS256 JWT, CORS, input validation
8. ✅ **Integration-Ready**: Works with existing Neon Postgres and RAG chatbot

**Gate Status**: ✅ PASS - Implementation approach aligns with all constitutional principles

---

## Architecture Decisions (ADRs)

### ADR-001: JWT Storage Strategy

**Decision**: Use **localStorage with HttpOnly cookie fallback** pattern

**Rationale**:
- localStorage: Easy access from JavaScript for local development/testing, simpler integration with react-hook-form
- HttpOnly cookie: Automatic security for production deployment
- Pattern: Implement both, client decides based on environment

**Alternatives Considered**:
- Pure localStorage: Vulnerable to XSS attacks (mitigated by input validation/CSP)
- Pure HttpOnly cookies: Requires session-based auth, more server overhead
- sessionStorage: Loses tokens on page close (UX issue for 7/30-day tokens)

**Implementation**:
- Frontend: Set token in localStorage on signup/signin
- Backend: Set HttpOnly cookie for production deployments
- Header: Include token in Authorization: Bearer {token} for API calls

**Related Spec**: FR-005, FR-006, FR-007

---

### ADR-002: Frontend State Management

**Decision**: Use **React Context API** for global auth state

**Rationale**:
- Docusaurus already uses React, no additional dependencies needed
- Simple auth state (user, token, loading) doesn't require Redux complexity
- Context.Provider wraps entire app in Root.js
- Reduces bundle size and implementation time

**Alternatives Considered**:
- Redux: Overkill for auth-only state, adds ~100KB bundle, longer learning curve
- Zustand: Lightweight alternative, but unnecessary for MVP scope
- Plain useState: Not shareable across components without prop drilling

**Implementation**:
- `AuthContext` (user, token, isLoading)
- `useAuth()` hook for components
- `AuthProvider` wrapper in Root.js

**Related Spec**: FR-001 through FR-022 (entire auth flow)

---

### ADR-003: Form Library & Validation

**Decision**: Use **react-hook-form + zod** for form handling and validation

**Rationale**:
- react-hook-form: Lightweight (8KB), minimal re-renders, minimal dependencies
- zod: Type-safe schema validation, works seamlessly with TypeScript
- Combination: Efficient client-side validation before API call
- Both battle-tested in production React applications

**Alternatives Considered**:
- Formik: Heavier (14KB), more overhead, steeper learning curve
- HTML5 validation: Insufficient for complex rules (password strength, duplicate email check)
- Custom validation: Error-prone, duplicates backend logic

**Implementation**:
- Zod schemas: signupSchema, signinSchema (in /types or /validators)
- react-hook-form: integrate in SignupPage and SigninPage components
- Real-time validation on blur, submit-time validation on submit

**Related Spec**: FR-002, FR-003 (validation requirements)

---

### ADR-004: Backend Authentication Library

**Decision**: Use **python-jose for JWT** + **passlib[bcrypt] for password hashing** (no fastapi-users)

**Rationale**:
- python-jose: Lightweight JWT library, explicit token creation/validation, full control
- passlib[bcrypt]: Industry-standard password hashing, no setup needed, works with any ORM
- Not using fastapi-users: Too opinionated (forces specific ORM/patterns), adds overhead for MVP
- Direct implementation: ~300 LOC backend auth code, clear and testable

**Alternatives Considered**:
- fastapi-users: Full-featured but opinionated, requires their models/schemas, harder to customize
- Manual JWT: Insecure if implemented wrong, python-jose handles edge cases properly
- Flask-Login: Overkill for stateless JWT approach

**Implementation**:
- `security.py`: Hash password function, verify password function, create token, verify token
- `user.py` model: User, UserBackground SQLAlchemy models
- `auth.py` routes: signup, signin, signout, get me, update profile endpoints

**Related Spec**: FR-004 (Bcrypt), FR-005 through FR-014 (JWT auth)

---

## Project Structure

### Documentation (this feature)

```text
specs/007-better-auth-authentication/
├── spec.md              # Feature specification
├── plan.md              # This file (implementation architecture)
├── research.md          # (Phase 0 - research findings)
├── data-model.md        # (Phase 1 - database schema + API contracts)
├── quickstart.md        # (Phase 1 - quick setup guide)
├── contracts/           # (Phase 1 - OpenAPI schemas)
│   └── auth-api.yaml
├── checklists/
│   └── requirements.md   # Quality validation checklist
└── tasks.md             # (Phase 2 - actionable development tasks)
```

### Frontend Source Code

```text
Front-End-Book/src/
├── components/
│   ├── TranslationButton/          # MODIFY: Add auth check
│   │   ├── index.tsx               # Add: useAuth() hook, guard
│   │   └── useTranslation.ts
│   ├── PersonalizationButton/      # MODIFY: Add auth check
│   │   └── index.tsx               # Add: useAuth() hook, guard
│   ├── Auth/                       # NEW
│   │   ├── SignupPage.tsx          # NEW: Signup form with bg questionnaire
│   │   ├── SigninPage.tsx          # NEW: Signin form with remember_me
│   │   ├── AuthProvider.tsx        # NEW: Context provider + useAuth hook
│   │   ├── ProtectedRoute.tsx      # NEW: Route guard component
│   │   ├── UserMenu.tsx            # NEW: Header user menu + profile link
│   │   └── ProfilePage.tsx         # NEW: Profile view/edit
│   └── RAGChatbot/                 # PRESERVE: No changes to chatbot
├── context/
│   └── AuthContext.ts              # NEW: Auth Context definition
├── hooks/
│   └── useAuth.ts                  # NEW: useAuth hook (returns context)
├── types/
│   ├── auth.ts                     # NEW: User, Token, LoginRequest types
│   └── api.ts                      # MODIFY: Add auth response types
├── services/
│   ├── authApi.ts                  # NEW: Signup, signin, profile API calls
│   └── api.ts                      # MODIFY: Add Authorization header to axios
├── theme/
│   ├── Root.js                     # MODIFY: Wrap with AuthProvider
│   └── DocItem/Content/index.js    # PRESERVE: No changes
└── styles/
    └── auth.module.css             # NEW: Auth component styles

tests/
├── components/
│   └── Auth/                       # NEW: Auth component tests
│       ├── SignupPage.test.tsx
│       ├── SigninPage.test.tsx
│       └── ProtectedRoute.test.tsx
└── services/
    └── authApi.test.ts             # NEW: Auth API service tests
```

### Backend Source Code

```text
backend/ (if separate, else add to existing FastAPI app)
├── app/
│   ├── main.py                     # MODIFY: Add auth routes
│   ├── models/
│   │   ├── user.py                 # NEW: User, UserBackground SQLAlchemy models
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── user.py                 # NEW: Pydantic schemas for user validation
│   │   ├── auth.py                 # NEW: SignupRequest, SigninRequest schemas
│   │   └── __init__.py
│   ├── routes/
│   │   ├── auth.py                 # NEW: signup, signin, signout endpoints
│   │   ├── users.py                # NEW: GET me, PUT profile endpoints
│   │   └── __init__.py
│   ├── security.py                 # NEW: Bcrypt + JWT utilities
│   ├── database.py                 # MODIFY: Add User + UserBackground tables
│   └── config.py                   # MODIFY: Add JWT_SECRET, JWT_ALGORITHM
├── tests/
│   ├── test_auth.py                # NEW: Signup/signin endpoint tests
│   ├── test_user.py                # NEW: Profile endpoint tests
│   └── conftest.py                 # NEW: Pytest fixtures
└── requirements.txt                # MODIFY: Add python-jose, passlib[bcrypt]
```

**Structure Decision**: Web application with separate frontend (Docusaurus/React) and backend (FastAPI) communicating via REST API. Frontend components handle UI/UX, backend provides auth logic and JWT tokens. Database shared (Neon Postgres).

---

## Data Model

### Database Entities

**User Table** (`users`)
```
id: UUID (PRIMARY KEY)
email: VARCHAR(255) UNIQUE NOT NULL
password_hash: VARCHAR(255) NOT NULL (Bcrypt hash)
full_name: VARCHAR(255) NOT NULL
created_at: TIMESTAMP DEFAULT now()
updated_at: TIMESTAMP DEFAULT now()
```

**UserBackground Table** (`user_backgrounds`)
```
id: UUID (PRIMARY KEY)
user_id: UUID (FOREIGN KEY → users.id, CASCADE DELETE)
software_background: VARCHAR(100) [e.g., "beginner", "intermediate", "advanced"]
hardware_background: VARCHAR(100) [e.g., "raspberry_pi", "jetson", "custom_pc"]
ros_experience: VARCHAR(50) [e.g., "none", "ros1_beginner", "ros2_intermediate"]
python_level: VARCHAR(50) [e.g., "beginner", "intermediate", "advanced", "expert"]
learning_goal: TEXT
available_hardware: TEXT [comma-separated or JSON list]
created_at: TIMESTAMP DEFAULT now()
updated_at: TIMESTAMP DEFAULT now()
CONSTRAINT: UNIQUE(user_id) [one background per user]
```

**AuthToken Table** (optional, for signout support) (`auth_tokens`)
```
id: UUID (PRIMARY KEY)
user_id: UUID (FOREIGN KEY → users.id, CASCADE DELETE)
token: VARCHAR(1000) NOT NULL
expires_at: TIMESTAMP NOT NULL
revoked: BOOLEAN DEFAULT FALSE
created_at: TIMESTAMP DEFAULT now()
```

### API Request/Response Contracts

**POST /api/auth/signup**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Smith",
  "software_background": "beginner",
  "hardware_background": "raspberry_pi",
  "ros_experience": "none",
  "python_level": "intermediate",
  "learning_goal": "Learn ROS2 fundamentals",
  "available_hardware": "Raspberry Pi 4"
}

Response (201 Created):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Smith"
  }
}

Error (400):
{
  "detail": "Email already registered" | "Password too weak" | "Validation error"
}
```

**POST /api/auth/signin**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "remember_me": false
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 604800 or 2592000 (if remember_me),
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Smith"
  }
}

Error (401):
{
  "detail": "Invalid email or password"
}
```

**GET /api/users/me** (requires Authorization: Bearer {token})
```
Response (200 OK):
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Smith",
  "background": {
    "software_background": "beginner",
    "hardware_background": "raspberry_pi",
    "ros_experience": "none",
    "python_level": "intermediate",
    "learning_goal": "Learn ROS2 fundamentals",
    "available_hardware": "Raspberry Pi 4"
  },
  "created_at": "2026-02-07T12:00:00Z"
}

Error (401):
{
  "detail": "Not authenticated"
}
```

**PUT /api/users/{user_id}** (requires Authorization: Bearer {token})
```json
Request (partial updates allowed):
{
  "full_name": "Jane Smith",
  "python_level": "advanced",
  "learning_goal": "Deploy ROS2 on cloud"
}

Response (200 OK):
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "Jane Smith",
  "background": { ... },
  "created_at": "2026-02-07T12:00:00Z",
  "updated_at": "2026-02-07T14:30:00Z"
}
```

**POST /api/auth/signout** (requires Authorization: Bearer {token})
```
Response (200 OK):
{
  "message": "Signed out successfully"
}
```

---

## Implementation Phases (Priority Order)

### Phase 1: Backend Foundation (2 hours)
- [ ] Create User + UserBackground SQLAlchemy models
- [ ] Implement security.py (hash_password, verify_password, create_access_token, verify_token)
- [ ] Implement POST /api/auth/signup endpoint
- [ ] Implement POST /api/auth/signin endpoint
- [ ] Implement GET /api/users/me endpoint (with JWT verification)
- [ ] Add CORS configuration (localhost:3000, localhost:8080)
- [ ] Database migrations: Create users and user_backgrounds tables in Neon Postgres

**Deliverable**: Backend API fully functional, tested with Postman/curl

### Phase 2: Frontend Components (2 hours)
- [ ] Create SignupPage component with react-hook-form + zod validation
- [ ] Create SigninPage component with remember_me checkbox
- [ ] Create AuthContext + AuthProvider (React Context)
- [ ] Create useAuth() hook
- [ ] Create ProtectedRoute component to guard routes
- [ ] Create UserMenu component (display name, profile link, signout button)
- [ ] Create ProfilePage component (view/edit profile info)

**Deliverable**: All auth UI components functional, responsive on mobile

### Phase 3: Integration (1 hour)
- [ ] Integrate AuthProvider in Root.js
- [ ] Modify TranslationButton to check auth status and show "Sign in to translate" prompt
- [ ] Modify PersonalizationButton to check auth status and show "Sign in to personalize" prompt
- [ ] Add auth routes to Docusaurus sidebar (signup, signin, profile pages)
- [ ] Test full flow: signup → auto-signin → use features → signout

**Deliverable**: Complete end-to-end auth flow working, no breaking changes to chatbot

### Phase 4: Polish & Testing (1 hour)
- [ ] Add error handling for expired tokens (401 responses)
- [ ] Implement token refresh/re-signin flow for expired sessions
- [ ] Add browser console error checking (no console errors in any flow)
- [ ] Mobile responsiveness testing (320px+ viewports)
- [ ] Write unit tests for authApi service, ProtectedRoute, useAuth hook
- [ ] Write integration tests for signup/signin backend endpoints

**Deliverable**: Production-ready auth system with 90%+ code coverage

---

## Testing Strategy

### Backend Unit Tests (pytest)
```
test_auth.py:
  - test_hash_password_creates_bcrypt_hash
  - test_verify_password_correct_password
  - test_verify_password_incorrect_password
  - test_create_access_token_7_day_default
  - test_create_access_token_30_day_with_remember_me
  - test_verify_token_valid_token
  - test_verify_token_expired_token
  - test_verify_token_invalid_token

test_user.py:
  - test_create_user_valid_email_password
  - test_create_user_duplicate_email_raises_error
  - test_create_user_weak_password_raises_error
  - test_get_user_by_email
  - test_get_user_by_id
  - test_update_user_profile
  - test_delete_user
```

### Backend Integration Tests (pytest)
```
test_endpoints.py:
  - test_signup_endpoint_returns_token
  - test_signup_endpoint_duplicate_email_returns_400
  - test_signin_endpoint_valid_credentials
  - test_signin_endpoint_invalid_credentials_returns_401
  - test_signin_remember_me_sets_30_day_expiry
  - test_get_me_endpoint_requires_token
  - test_get_me_endpoint_returns_user_info
  - test_update_profile_endpoint_updates_fields
  - test_update_profile_endpoint_requires_token
  - test_signout_endpoint_invalidates_token (if token revocation implemented)
  - test_cors_headers_present_for_allowed_origins
```

### Frontend Component Tests (React Testing Library)
```
SignupPage.test.tsx:
  - test_renders_signup_form
  - test_validates_email_format
  - test_validates_password_strength
  - test_submits_form_on_valid_input
  - test_shows_error_on_duplicate_email
  - test_auto_signs_in_on_success

SigninPage.test.tsx:
  - test_renders_signin_form
  - test_submits_form_on_valid_input
  - test_shows_error_on_invalid_credentials
  - test_remember_me_checkbox_works
  - test_redirects_to_home_on_success

ProtectedRoute.test.tsx:
  - test_renders_component_if_authenticated
  - test_redirects_to_signin_if_unauthenticated
  - test_redirects_on_token_expiry

useAuth.test.ts:
  - test_returns_null_user_if_no_token
  - test_returns_user_if_token_valid
  - test_provides_logout_function
```

### E2E Tests (Manual or Playwright)
```
test_complete_auth_flow:
  1. Start unauthenticated
  2. Navigate to /signup
  3. Fill signup form with all background fields
  4. Submit → verify auto-signin
  5. Verify user name in header
  6. Navigate to protected feature (Translation button)
  7. Click button → API call includes JWT token
  8. Navigate to /profile
  9. Update profile field
  10. Verify change persisted
  11. Click signout
  12. Verify redirected to signin
  13. Verify protected features now show "Sign in" prompt
```

---

## Deployment Steps

### Backend Deployment (FastAPI on existing server)

1. **Environment Setup**
   ```bash
   # Add to .env or secrets management
   JWT_SECRET=<generate-random-secret-key>
   JWT_ALGORITHM=HS256
   DATABASE_URL=<existing-neon-postgres-url>
   CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
   ```

2. **Database Migrations**
   ```bash
   # Using Alembic (if set up) or direct SQL
   CREATE TABLE users (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     email VARCHAR(255) UNIQUE NOT NULL,
     password_hash VARCHAR(255) NOT NULL,
     full_name VARCHAR(255) NOT NULL,
     created_at TIMESTAMP DEFAULT now(),
     updated_at TIMESTAMP DEFAULT now()
   );

   CREATE TABLE user_backgrounds (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     user_id UUID REFERENCES users(id) ON DELETE CASCADE,
     software_background VARCHAR(100),
     hardware_background VARCHAR(100),
     ros_experience VARCHAR(50),
     python_level VARCHAR(50),
     learning_goal TEXT,
     available_hardware TEXT,
     created_at TIMESTAMP DEFAULT now(),
     updated_at TIMESTAMP DEFAULT now(),
     UNIQUE(user_id)
   );
   ```

3. **Install Dependencies**
   ```bash
   pip install python-jose[cryptography] passlib[bcrypt] fastapi sqlalchemy pydantic
   ```

4. **Start Backend**
   ```bash
   uvicorn main:app --reload  # Development
   # OR
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app  # Production
   ```

5. **Verify Endpoints**
   ```bash
   curl -X POST http://localhost:8000/api/auth/signup \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"Test1234","full_name":"Test User",...}'
   ```

### Frontend Deployment (Docusaurus on localhost:3000)

1. **Install Dependencies**
   ```bash
   npm install react-hook-form zod axios
   ```

2. **Build Frontend**
   ```bash
   npm run build
   npm run serve  # Preview production build
   ```

3. **Configure API Endpoint**
   ```
   # In .env or environment config
   REACT_APP_API_URL=http://localhost:8000  # or deployed backend URL
   ```

4. **Start Dev Server**
   ```bash
   npm run start
   ```

5. **Verify Frontend**
   - Navigate to http://localhost:3000/signup
   - Fill form → Submit → Verify JWT token in localStorage
   - Verify user name in header
   - Test protected features

### Integration Testing

1. **Test Auth Flow End-to-End**
   - Signup with test account
   - Signin with test account
   - Use protected features (Translation, Personalization)
   - Signout

2. **Check for Console Errors**
   - Open DevTools (F12)
   - Go to Console tab
   - Perform all auth actions
   - Verify zero errors

3. **Verify No Breaking Changes**
   - Test RAG chatbot functionality
   - Test existing features (non-auth)
   - Verify Docusaurus routing still works

---

## Implementation Timeline (5-8 hours breakdown)

| Phase | Task | Est. Time | Cumulative |
|-------|------|-----------|-----------|
| **Setup** | Clone branch, install dependencies, database schema review | 30 min | 0:30 |
| **Phase 1** | Backend models + security.py + signup/signin endpoints | 2 hours | 2:30 |
| **Phase 1** | Get /me + CORS + database migrations | 30 min | 3:00 |
| **Phase 2** | SignupPage + SigninPage components | 1 hour | 4:00 |
| **Phase 2** | AuthContext + AuthProvider + useAuth hook | 45 min | 4:45 |
| **Phase 2** | ProtectedRoute + UserMenu + ProfilePage | 45 min | 5:30 |
| **Phase 3** | Integration: Root.js + TranslationButton + PersonalizationButton | 30 min | 6:00 |
| **Phase 3** | Testing full flow + documentation | 30 min | 6:30 |
| **Phase 4** | Error handling + token expiry logic + console checks | 30 min | 7:00 |
| **Phase 4** | Unit tests + final review + deployment | 1 hour | 8:00 |
| **Contingency** | Bug fixes, edge cases, polish | - | 8:00 |

**Total**: 5-8 hours (MVP can ship at 6 hours, polish extends to 8)

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| JWT token expires during user session | Medium | User can't use protected features | Implement token refresh endpoint; show "session expired" prompt; prompt to re-signin |
| Existing chatbot breaks | Low | Feature doesn't ship | Test chatbot flows end-to-end; use separate auth context to avoid affecting other components |
| Password hashing performance issues | Very Low | Signup/signin slow | Use Bcrypt with salt rounds=10 (standard); performance typically <100ms |
| CORS misconfiguration | Medium | Frontend can't call backend API | Test CORS headers with curl; verify Access-Control-Allow-Origin in FastAPI response |
| Database connection drops | Low | All auth operations fail | Add connection retry logic; use existing Neon Postgres connection pooling |
| Mobile layout breaks | Medium | Users on mobile can't sign up | Use Tailwind/flex for responsive design; test on 320px viewport |

---

## Next Steps

1. **Proceed to Phase 0: Research** (`/sp.plan research` or continue with Phase 1)
2. **Generate Data Model & API Contracts** (`data-model.md`, `contracts/`)
3. **Create Quick Start Guide** (`quickstart.md`)
4. **Generate Tasks** (`/sp.tasks` - creates `tasks.md` with actionable development tasks)

---

## Related Artifacts

- **Specification**: `spec.md` (5 user stories, 22 requirements, 13 success criteria)
- **Quality Checklist**: `checklists/requirements.md` (all passing)
- **Research Findings**: `research.md` (Phase 0 - if generated)
- **Data Model**: `data-model.md` (Phase 1 - if generated)
- **API Contracts**: `contracts/auth-api.yaml` (Phase 1 - if generated)
- **Tasks**: `tasks.md` (Phase 2 - generated by `/sp.tasks`)
