# Development Tasks: Better-Auth Authentication System

**Feature**: Better-Auth Authentication System (007)
**Branch**: `007-better-auth-authentication`
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)
**Target**: 50 hackathon bonus points | **Timeline**: 5-8 hours
**Status**: Ready for implementation

---

## Task Organization & Strategy

**User Stories** (from spec.md - Priority Order):
- **[US1]** User Story 1: New User Registration with Background Profile (P1)
- **[US2]** User Story 2: Existing User Sign In (P1)
- **[US3]** User Story 3: Protected Translation & Personalization Features (P1)
- **[US4]** User Story 4: User Profile Management (P2)
- **[US5]** User Story 5: Sign Out (P2)

**Implementation Strategy**:
- **MVP Scope** (6 hours): Complete US1 + US2 + US3 (core auth flow + feature protection)
- **Extended** (8 hours): Add US4 + US5 (profile management + signout)
- **Parallelization**: Backend and frontend can be developed in parallel after Phase 2

**Independent Test Criteria**:
- [US1] ✅ Testable: Signup form → submit → verify user created + auto-signin ✓
- [US2] ✅ Testable: Signin form → submit → verify JWT token + user in header ✓
- [US3] ✅ Testable: Protected button → unauthenticated shows prompt, authenticated calls API ✓
- [US4] ✅ Testable: Profile page → edit fields → verify persistence ✓
- [US5] ✅ Testable: Signout button → verify token cleared + protected features disabled ✓

---

## Phase 1: Setup & Infrastructure (30 minutes)

### Project Initialization & Dependencies

- [ ] T001 Install backend dependencies: `pip install python-jose[cryptography] passlib[bcrypt] fastapi sqlalchemy pydantic` in requirements.txt
- [ ] T002 Install frontend dependencies: `npm install react-hook-form zod axios` in Front-End-Book/
- [ ] T003 Create backend directory structure: `backend/app/{models,schemas,routes,security}` directories
- [ ] T004 Create frontend directory structure: `Front-End-Book/src/{components/Auth,context,hooks,services,types}`
- [ ] T005 Set up environment variables: Add JWT_SECRET, JWT_ALGORITHM, DATABASE_URL, CORS_ORIGINS to .env or config.py
- [ ] T006 Verify existing Neon Postgres connection is working: Test connection string in config.py

---

## Phase 2: Foundational Backend (1 hour)

### Database Models & Security Infrastructure

- [ ] T007 [P] Create User SQLAlchemy model in `backend/app/models/user.py`:
  - Fields: id (UUID), email (unique), password_hash, full_name, created_at, updated_at
  - Indexes on email for lookups
  - Relationship to UserBackground

- [ ] T008 [P] Create UserBackground SQLAlchemy model in `backend/app/models/user.py`:
  - Fields: id, user_id (FK), software_background, hardware_background, ros_experience, python_level, learning_goal, available_hardware
  - Relationship back to User (cascade delete)

- [ ] T009 [P] Implement security utilities in `backend/app/security.py`:
  - `hash_password(password: str) -> str` using passlib[bcrypt]
  - `verify_password(plain: str, hashed: str) -> bool`
  - `create_access_token(user_id: str, remember_me: bool = False) -> str` (7-day or 30-day expiry)
  - `verify_token(token: str) -> str` (returns user_id or raises exception)
  - Test: password hashing produces Bcrypt hash, verify works correctly

- [ ] T010 [P] Implement Pydantic validation schemas in `backend/app/schemas/`:
  - `SignupRequest` (email, password, full_name, software_background, hardware_background, ros_experience, python_level, learning_goal, available_hardware)
  - `SigninRequest` (email, password, remember_me)
  - `UserResponse` (id, email, full_name, background, created_at)
  - `TokenResponse` (access_token, token_type, expires_in, user)

- [ ] T011 Create database migration/initialization script in `backend/app/database.py`:
  - Initialize SQLAlchemy engine with Neon Postgres connection
  - Create users and user_backgrounds tables
  - Test: Tables created successfully in Neon Postgres

- [ ] T012 Add CORS configuration in `backend/app/main.py`:
  - Enable CORS for localhost:3000 and localhost:8080
  - Allow Authorization headers

---

## Phase 3: Backend User Story Implementation

### User Story 1 & 2: Authentication Endpoints (Signup/Signin)

**US1 & US2 Share Backend Infrastructure - Implement Together**

- [ ] T013 [P] [US1][US2] Implement POST `/api/auth/signup` endpoint in `backend/app/routes/auth.py`:
  - Accept SignupRequest (email, password, full_name, bg fields)
  - Validate email format (regex)
  - Validate password strength (8+ chars, uppercase, lowercase, number)
  - Check email not already registered
  - Hash password using security.hash_password()
  - Create User record in database
  - Create UserBackground record
  - Generate JWT token using security.create_access_token()
  - Return TokenResponse + user info
  - Error handling: 400 for validation, 409 for duplicate email

- [ ] T014 [P] [US1][US2] Implement POST `/api/auth/signin` endpoint in `backend/app/routes/auth.py`:
  - Accept SigninRequest (email, password, remember_me)
  - Look up user by email
  - Verify password using security.verify_password()
  - If remember_me: create 30-day token, else 7-day token
  - Return TokenResponse + user info
  - Error handling: 401 for invalid credentials (generic message)

- [ ] T015 [P] [US2] Implement GET `/api/users/me` endpoint in `backend/app/routes/users.py`:
  - Require valid JWT in Authorization header
  - Extract user_id from token
  - Return UserResponse (user + background info)
  - Error handling: 401 if no token or invalid token

- [ ] T016 [US1][US2] Create JWT middleware/dependency in `backend/app/security.py`:
  - `get_current_user(token: str) -> str` FastAPI dependency
  - Extracts and validates JWT token from Authorization header
  - Used in protected endpoints

- [ ] T017 [US1][US2] Write backend unit tests in `backend/tests/test_auth.py`:
  - Test password hashing (hash_password creates valid Bcrypt)
  - Test password verification (correct/incorrect passwords)
  - Test JWT token creation (7-day default)
  - Test JWT token creation (30-day with remember_me)
  - Test JWT token verification (valid/invalid/expired tokens)
  - Run: `pytest backend/tests/test_auth.py`

- [ ] T018 [US1][US2] Write backend integration tests in `backend/tests/test_endpoints.py`:
  - Test POST /signup with valid data → user created + token returned
  - Test POST /signup with duplicate email → 409 error
  - Test POST /signup with weak password → 400 error
  - Test POST /signin with valid credentials → token returned
  - Test POST /signin with invalid password → 401 error
  - Test GET /me with valid token → user info returned
  - Test GET /me without token → 401 error
  - Run: `pytest backend/tests/test_endpoints.py`

---

### User Story 3: Protected Features (Feature Guards)

- [ ] T019 [US3] Implement PUT `/api/users/{user_id}` endpoint in `backend/app/routes/users.py`:
  - Require valid JWT in Authorization header
  - Allow partial updates (full_name, password, background fields)
  - Return updated UserResponse
  - Error handling: 401 if not authenticated, 403 if trying to update another user

- [ ] T020 [US3] Implement authorization middleware decorator in `backend/app/security.py`:
  - `@require_auth` decorator for endpoints
  - Validates JWT token
  - Adds current_user to request context
  - Used in protected endpoints (/api/translate, /api/personalize)

- [ ] T021 [US3] Add JWT requirement to translation endpoint in `backend/app/routes/` (or wherever existing):
  - Add @require_auth decorator
  - Extract JWT from Authorization header
  - Only process if valid JWT present
  - Return 401 if missing/invalid JWT

- [ ] T022 [US3] Add JWT requirement to personalization endpoint:
  - Add @require_auth decorator
  - Extract JWT from Authorization header
  - Only process if valid JWT present
  - Return 401 if missing/invalid JWT

---

### User Story 4: Profile Management (Extended Scope)

- [ ] T023 [P] [US4] Implement GET `/api/users/{user_id}` endpoint (retrieve profile):
  - Require valid JWT
  - Return full user profile (email, name, background fields, created_at, updated_at)
  - Error handling: 401 if not authenticated, 403 if accessing another user's profile (unless admin)

- [ ] T024 [US4] Implement password update logic in `backend/app/routes/users.py`:
  - Add endpoint or extend PUT /users/{user_id} to accept password changes
  - Require old password verification before setting new password
  - Hash new password using security.hash_password()
  - Invalidate all existing tokens for user (if token revocation implemented)

- [ ] T025 [US4] Write profile management tests in `backend/tests/test_profile.py`:
  - Test GET /users/me returns full profile
  - Test PUT /users/{user_id} updates fields
  - Test PUT /users/{user_id} rejects unauthorized updates
  - Run: `pytest backend/tests/test_profile.py`

---

### User Story 5: Sign Out (Extended Scope)

- [ ] T026 [US5] Implement POST `/api/auth/signout` endpoint in `backend/app/routes/auth.py`:
  - Require valid JWT
  - Optional: Invalidate token in auth_tokens table (if implemented)
  - Return success message: `{"message": "Signed out successfully"}`
  - Error handling: 401 if not authenticated

- [ ] T027 [US5] Test signout endpoint:
  - Test POST /signout with valid JWT → success response
  - Test POST /signout without JWT → 401 error

---

## Phase 4: Frontend User Story Implementation

### Foundational Frontend (Auth Context & Utilities)

- [ ] T028 [P] Create AuthContext in `Front-End-Book/src/context/AuthContext.ts`:
  - Define AuthContext with user, token, isLoading, error state
  - Define AuthProvider component
  - Provide signup, signin, signout, getProfile actions
  - Use localStorage for token persistence
  - Test: Context exports and Provider wraps app

- [ ] T029 [P] Create useAuth hook in `Front-End-Book/src/hooks/useAuth.ts`:
  - Export useAuth() hook that returns context value
  - Throw error if used outside AuthProvider
  - Test: Hook returns context values correctly

- [ ] T030 [P] Create authApi service in `Front-End-Book/src/services/authApi.ts`:
  - `signup(email, password, full_name, bgData)` → calls POST /api/auth/signup
  - `signin(email, password, rememberMe)` → calls POST /api/auth/signin
  - `getMe()` → calls GET /api/users/me (requires JWT)
  - `updateProfile(data)` → calls PUT /api/users/{user_id}
  - `signout()` → calls POST /api/auth/signout (requires JWT)
  - All methods include JWT in Authorization header
  - Error handling: catch and return error objects

- [ ] T031 [P] Create validation schemas in `Front-End-Book/src/types/auth.ts`:
  - `signupSchema` (zod): email (valid format), password (8+ chars, uppercase, lowercase, number), full_name, bg fields
  - `signinSchema` (zod): email (valid format), password (not empty)
  - `profileSchema` (zod): full_name, python_level, learning_goal (optional fields)
  - Test: Schemas validate correct/incorrect inputs

- [ ] T032 [P] Create auth types in `Front-End-Book/src/types/auth.ts`:
  - `User` type: id, email, full_name, background, created_at
  - `AuthContextType` type: user, token, isLoading, error, signin, signup, signout functions
  - `SignupRequest`, `SigninRequest`, `TokenResponse` types

- [ ] T033 Modify axios instance in `Front-End-Book/src/services/api.ts`:
  - Create axios instance with base URL (http://localhost:8000/api)
  - Add request interceptor to include JWT token in Authorization header
  - Add response interceptor to handle 401 responses (redirect to signin)

---

### User Story 1: Signup Page (Frontend)

- [ ] T034 [P] [US1] Create SignupPage component in `Front-End-Book/src/components/Auth/SignupPage.tsx`:
  - Use react-hook-form + signupSchema
  - Form fields: email, password (show strength indicator), confirm password, full_name
  - Background questionnaire fields: software_background (select), hardware_background (select), ros_experience (select), python_level (select), learning_goal (textarea), available_hardware (text)
  - Submit button: Call authApi.signup() with form data
  - On success: auto-signin, store token in context + localStorage, redirect to home
  - On error: Display error message (email already registered, validation errors, server errors)
  - Style: Mobile responsive (320px+), clean form layout
  - Test: Form renders, validates, submits successfully

- [ ] T035 [P] [US1] Create password strength indicator in `Front-End-Book/src/components/Auth/PasswordStrength.tsx`:
  - Visual indicator: Weak (red), Fair (yellow), Strong (green)
  - Rules: 8+ chars, uppercase, lowercase, number
  - Display in real-time as user types
  - Test: Shows correct strength based on input

- [ ] T036 [US1] Write frontend component tests for SignupPage in `Front-End-Book/src/components/Auth/__tests__/SignupPage.test.tsx`:
  - Test form renders all fields
  - Test email validation (invalid format rejected)
  - Test password validation (weak password rejected, strength indicator works)
  - Test form submission with valid data
  - Test error display for duplicate email
  - Test auto-signin on success
  - Run: `npm test SignupPage`

---

### User Story 2: Signin Page (Frontend)

- [ ] T037 [P] [US2] Create SigninPage component in `Front-End-Book/src/components/Auth/SigninPage.tsx`:
  - Use react-hook-form + signinSchema
  - Form fields: email, password
  - Checkbox: "Remember me" (30-day token)
  - Submit button: Call authApi.signin() with form data
  - On success: Store token in context + localStorage, redirect to home
  - On error: Display generic error "Invalid email or password" (security best practice)
  - Link to signup page: "Don't have an account? Sign up"
  - Style: Mobile responsive, clean form layout
  - Test: Form renders, validates, submits successfully

- [ ] T038 [P] [US2] Create UserMenu component in `Front-End-Book/src/components/Auth/UserMenu.tsx`:
  - Display authenticated user's full_name in header
  - Dropdown menu: Profile link, Signout button
  - When unauthenticated: Show "Sign In" link
  - Style: Responsive, works in header
  - Test: Shows name when authenticated, shows signin link when unauthenticated

- [ ] T039 [US2] Write frontend component tests for SigninPage in `Front-End-Book/src/components/Auth/__tests__/SigninPage.test.tsx`:
  - Test form renders email and password fields
  - Test remember_me checkbox functionality
  - Test form submission with valid credentials
  - Test generic error message for invalid credentials
  - Test redirect on success
  - Run: `npm test SigninPage`

- [ ] T040 [US2] Write frontend component tests for UserMenu in `Front-End-Book/src/components/Auth/__tests__/UserMenu.test.tsx`:
  - Test displays user name when authenticated
  - Test shows signin link when unauthenticated
  - Test profile link functional
  - Test signout button calls signout function
  - Run: `npm test UserMenu`

---

### User Story 3: Protected Features (Frontend)

- [ ] T041 [P] [US3] Create ProtectedRoute component in `Front-End-Book/src/components/Auth/ProtectedRoute.tsx`:
  - Check if user is authenticated (useAuth hook)
  - If yes: Render children normally
  - If no: Show error boundary or redirect to signin
  - Used for protecting /profile route

- [ ] T042 [P] [US3] Modify TranslationButton component in `Front-End-Book/src/components/TranslationButton/index.tsx`:
  - Import useAuth hook
  - Check if user authenticated
  - If not authenticated: Show tooltip "Sign in to translate to Urdu", disable button, on click show signin prompt
  - If authenticated: Enable button, normal translation flow
  - Include JWT token in translation API call (handled by axios interceptor)
  - Test: Unauthenticated shows prompt, authenticated enables button

- [ ] T043 [P] [US3] Modify PersonalizationButton component:
  - Import useAuth hook
  - Check if user authenticated
  - If not authenticated: Show tooltip "Sign in to personalize your experience", disable button
  - If authenticated: Enable button, normal personalization flow
  - Include JWT token in personalization API call
  - Test: Unauthenticated shows prompt, authenticated enables button

- [ ] T044 [US3] Write frontend component tests for ProtectedRoute:
  - Test renders children if authenticated
  - Test redirects/shows error if not authenticated
  - Run: `npm test ProtectedRoute`

- [ ] T045 [US3] Test protected feature endpoints:
  - Test TranslationButton sends JWT token to /api/translate
  - Test PersonalizationButton sends JWT token to /api/personalize
  - Test 401 response when JWT missing/invalid redirects to signin
  - Manual test: Click buttons unauthenticated (see prompt) vs authenticated (see action)

---

### User Story 4: Profile Page (Extended Scope)

- [ ] T046 [P] [US4] Create ProfilePage component in `Front-End-Book/src/components/Auth/ProfilePage.tsx`:
  - Use ProtectedRoute wrapper
  - Display current user info (email, full_name, created_at)
  - Edit form fields: full_name, software_background, hardware_background, ros_experience, python_level, learning_goal, available_hardware
  - Submit button: Call authApi.updateProfile() with form data
  - On success: Update context, show success message
  - On error: Display error message
  - Style: Mobile responsive, clean form layout
  - Test: Form renders, loads current data, submits successfully

- [ ] T047 [P] [US4] Create password change form in ProfilePage or separate component:
  - Fields: current_password, new_password, confirm_password
  - Validation: Current password must be correct, new password must meet strength rules
  - Submit: Call authApi.updatePassword() with passwords
  - On success: Show success message, clear form
  - On error: Show error message (incorrect current password, validation errors)
  - Security: Don't auto-fill password fields
  - Test: Form validation works, password change successful

- [ ] T048 [US4] Write frontend component tests for ProfilePage:
  - Test page loads user data
  - Test form fields can be edited
  - Test submit updates profile
  - Test password change works (with validation)
  - Run: `npm test ProfilePage`

---

### User Story 5: Sign Out (Extended Scope)

- [ ] T049 [P] [US5] Implement signout function in AuthContext:
  - Call authApi.signout() to notify backend
  - Clear token from localStorage
  - Clear user from context state
  - Redirect to home page
  - Error handling: Show error if API call fails, still clear local state

- [ ] T050 [US5] Create Signout confirmation in UserMenu:
  - Optional: Show confirmation dialog before signout
  - On confirm: Call authContext.signout()
  - Redirect to home page
  - Test: Signout clears token and state

---

## Phase 5: Integration & Final Testing

### Integration & Routing

- [ ] T051 [P] Wrap app with AuthProvider in `Front-End-Book/src/theme/Root.js`:
  - Import AuthProvider from context/AuthContext
  - Wrap entire app with `<AuthProvider><RootContent>{children}</RootContent></AuthProvider>`
  - Ensure AuthProvider is outside other providers/context

- [ ] T052 Add auth routes to Docusaurus routing in `Front-End-Book/sidebars.js` or routing config:
  - Add `/signup` route → SignupPage
  - Add `/signin` route → SigninPage
  - Add `/profile` route → ProfilePage (protected with ProtectedRoute)
  - Ensure proper navigation links in navbar

- [ ] T053 Test complete user flow end-to-end:
  - Start app (npm run start)
  - Navigate to /signup
  - Fill signup form with all background fields
  - Submit → verify user created in database
  - Verify auto-signin (JWT in localStorage, user in header)
  - Navigate to home page
  - Click TranslationButton → verify API call includes JWT token
  - Navigate to /profile
  - Update profile field → verify change persisted
  - Click Signout → verify token cleared, protected features disabled
  - Navigate to /signin
  - Signin with credentials → verify JWT token issued
  - Manual walkthrough: No console errors, mobile responsive

---

### Browser Console & Quality Checks

- [ ] T054 Verify zero console errors in dev tools:
  - Open DevTools (F12)
  - Go to Console tab
  - Perform all auth actions (signup, signin, profile, signout)
  - **Acceptance**: Zero errors, warnings only for deprecation
  - Document any warnings and suppress if necessary

- [ ] T055 Mobile responsiveness testing (320px viewport):
  - Test signup form on mobile: All fields visible, buttons clickable
  - Test signin form on mobile: All fields visible, buttons clickable
  - Test profile page on mobile: All fields visible, update button clickable
  - Test user menu on mobile: Dropdown works, signout clickable
  - **Acceptance**: No layout breaks, no horizontal scrolling, all touch targets 44px+

- [ ] T056 Test no breaking changes to RAG chatbot:
  - Load app with chatbot enabled
  - Verify chatbot floating button visible
  - Click chatbot button → verify chat opens
  - Type message → verify chatbot responds
  - **Acceptance**: Chatbot functionality unchanged, no errors

---

### Documentation & Handoff

- [ ] T057 Document setup instructions in `SETUP.md`:
  - Backend setup (install dependencies, env vars, database migrations, start uvicorn)
  - Frontend setup (install dependencies, env vars, npm run start)
  - API endpoints documentation (all 5 endpoints with examples)
  - Testing instructions (unit tests, integration tests, E2E)
  - Known limitations and future enhancements

- [ ] T058 Add TypeScript types documentation:
  - Document User, AuthContext, SignupRequest types in JSDoc
  - Export all types from `types/auth.ts` for reuse
  - Ensure IDE auto-complete works for auth objects

- [ ] T059 Create API documentation in `API.md`:
  - Document all 5 endpoints: POST /signup, POST /signin, GET /users/me, PUT /users/{user_id}, POST /signout
  - Show request/response examples for each
  - Document error codes and messages
  - Include JWT token format and expiry times

---

## Parallel Execution Opportunities

### Can Run in Parallel After T006 (Setup):

**Backend Track** (Team Member 1):
1. T007, T008 (models) → parallel
2. T009 (security) + T010 (schemas) → can start after models
3. T011, T012 (database setup) → parallel to endpoints
4. T013, T014, T015 (endpoints) → parallel backend dev
5. T016, T017, T018 (tests) → parallel testing

**Frontend Track** (Team Member 2):
1. T028, T029, T030, T031, T032, T033 (foundational) → can start immediately
2. T034, T035, T036 (signup) → parallel to signin
3. T037, T038, T039, T040 (signin) → parallel to signup
4. T041, T042, T043, T044, T045 (protected features) → after core components

**Integration** (After both tracks):
1. T051, T052, T053 (integration)
2. T054, T055, T056 (quality checks)
3. T057, T058, T059 (documentation)

### Estimated Parallel Timeline:
- **Parallel Backend + Frontend**: 3-4 hours (instead of 5-6 sequential)
- **Integration + Testing**: 1-2 hours
- **Total**: 4-6 hours (vs 5-8 sequential)

---

## Task Completion Checklist

### MVP Scope (6 hours) - REQUIRED FOR HACKATHON:
- [ ] Phase 1: Setup (T001-T006)
- [ ] Phase 2: Backend Foundation (T007-T012)
- [ ] User Story 1 Backend (T013, T017-T018)
- [ ] User Story 2 Backend (T014-T015, T017-T018)
- [ ] User Story 3 Backend (T019-T022)
- [ ] User Story 1 Frontend (T028-T040, T034-T040)
- [ ] User Story 2 Frontend (T037-T040)
- [ ] User Story 3 Frontend (T041-T045)
- [ ] Integration (T051-T053)
- [ ] Quality (T054-T056)

### Extended Scope (8 hours) - BONUS:
- [ ] User Story 4 Backend (T023-T025)
- [ ] User Story 4 Frontend (T046-T048)
- [ ] User Story 5 Backend (T026-T027)
- [ ] User Story 5 Frontend (T049-T050)
- [ ] Documentation (T057-T059)

---

## Success Metrics

| Criterion | Target | Status |
|-----------|--------|--------|
| Signup works with background questionnaire | ✓ Auto-signin after signup | ⏳ |
| Signin works with 7-day/30-day tokens | ✓ JWT token valid | ⏳ |
| Protected features work (Translation, Personalization) | ✓ Require JWT in API call | ⏳ |
| Profile management works (US4) | ✓ View/edit profile | ⏳ |
| Signout works (US5) | ✓ Token cleared | ⏳ |
| Mobile responsive | ✓ 320px+ viewport | ⏳ |
| Zero console errors | ✓ DevTools console clean | ⏳ |
| No breaking changes to chatbot | ✓ Chatbot still functional | ⏳ |
| Hackathon bonus points | ✓ 50 points | ⏳ |

---

## Related Documents

- **Specification**: [spec.md](spec.md) (5 user stories, 22 requirements, 13 success criteria)
- **Implementation Plan**: [plan.md](plan.md) (tech stack, architecture, phases, timeline)
- **Quality Checklist**: [checklists/requirements.md](checklists/requirements.md) (all items passing)
