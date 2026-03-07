# Feature Specification: Better-Auth Authentication System

**Feature Branch**: `007-better-auth-authentication`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Implement user authentication using better-auth library to protect translation and personalization features in a Physical AI textbook (Docusaurus + FastAPI + Neon Postgres). Signup: email, password, full_name + background questionnaire. Signin: JWT tokens (7-day expiry, 30-day with remember_me). Profile: GET/UPDATE endpoints. Protection: TranslationButton and PersonalizationButton require authentication. Database: Users table in existing Neon Postgres. Security: Bcrypt password hashing, JWT with HS256, CORS for localhost:3000 and localhost:8080."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - New User Registration with Background Profile (Priority: P1)

A new user discovers the textbook and wants to access translation features. They must sign up with their email, password, and background information to unlock personalized learning features.

**Why this priority**: User account creation is the foundational feature - without it, no authentication or personalization is possible. This is the entry point for all new users.

**Independent Test**: Can be fully tested by navigating to signup form, entering valid credentials and background info, submitting, and verifying successful account creation with auto-signin.

**Acceptance Scenarios**:

1. **Given** a new user on the signup page, **When** they enter email, password, full name, and background questionnaire (software_background, hardware_background, ros_experience, python_level, learning_goal, available_hardware), **Then** the account is created and they are automatically signed in with a valid JWT token displayed.

2. **Given** an existing user attempts to sign up with an already-registered email, **When** they submit the form, **Then** they receive a clear error message "This email is already registered" and the account is not created.

3. **Given** a user enters an invalid email format during signup, **When** they submit, **Then** they receive a validation error "Please enter a valid email address" before submission.

4. **Given** a user enters a password with insufficient strength during signup, **When** they attempt submission, **Then** they see a clear requirement message: "Password must be at least 8 characters with uppercase, lowercase, and numbers."

5. **Given** a new user successfully signs up, **When** they refresh the page, **Then** they remain signed in (JWT token persisted and valid).

---

### User Story 2 - Existing User Sign In (Priority: P1)

An existing user wants to access the textbook and its protected features. They sign in with email and password, and the system provides them with authentication tokens and displays their name in the header.

**Why this priority**: Signin is equally critical as signup - registered users must be able to authenticate to access protected features. This is the primary interaction for returning users.

**Independent Test**: Can be fully tested by signing in with valid credentials and verifying JWT token issuance, token validity (7-day default or 30-day with remember_me), and user context availability in the header.

**Acceptance Scenarios**:

1. **Given** a registered user on the signin page, **When** they enter their correct email and password, **Then** they receive a valid JWT token (7-day expiry by default) and are redirected to the home page.

2. **Given** a user on the signin page with the "Remember me" option checked, **When** they enter valid credentials, **Then** they receive a JWT token with a 30-day expiry instead of 7 days.

3. **Given** a signed-in user viewing the page header, **When** the page loads, **Then** they see their full name displayed in the user menu (e.g., "Welcome, John Smith").

4. **Given** a user attempts signin with an incorrect password, **When** they submit the form, **Then** they see an error message "Invalid email or password" without revealing which field is wrong (security best practice).

5. **Given** a user attempts signin with an unregistered email, **When** they submit, **Then** they see the same generic error "Invalid email or password".

---

### User Story 3 - Protected Translation & Personalization Features (Priority: P1)

Unauthenticated users encounter the translation and personalization buttons but cannot use them. Authenticated users can click these buttons freely. This protects premium features behind authentication.

**Why this priority**: Feature protection is a core requirement - without it, non-registered users can access translation and personalization. This directly supports the hackathon bonus points.

**Independent Test**: Can be fully tested by verifying TranslationButton and PersonalizationButton behavior (disabled/prompt for unauthenticated, functional for authenticated users).

**Acceptance Scenarios**:

1. **Given** an unauthenticated user viewing a page with the TranslationButton, **When** they hover over or attempt to click it, **Then** they see a tooltip/prompt "Sign in to translate to Urdu" instead of the normal translation action.

2. **Given** an unauthenticated user viewing the PersonalizationButton, **When** they attempt to interact with it, **Then** they see "Sign in to personalize your experience" prompt.

3. **Given** an authenticated user with a valid JWT token, **When** they click the TranslationButton, **Then** the translation API is called with their JWT token included in the Authorization header.

4. **Given** an authenticated user with a valid JWT token, **When** they click the PersonalizationButton, **Then** the personalization API is called with their JWT token included.

5. **Given** a user whose JWT token has expired, **When** they attempt to use a protected feature, **Then** they see a message "Your session has expired. Please sign in again" and are prompted to re-authenticate.

---

### User Story 4 - User Profile Management (Priority: P2)

An authenticated user can view and update their profile information, including email, password, and background information collected during signup.

**Why this priority**: Profile management enhances user control and personalization but is not required for core MVP. Users can access the app without updating their profile.

**Independent Test**: Can be fully tested by signin, navigating to profile page, updating profile fields, and verifying changes persist and are reflected across the app.

**Acceptance Scenarios**:

1. **Given** an authenticated user on their profile page, **When** the page loads, **Then** all their profile fields are pre-populated (email, full_name, background questionnaire fields).

2. **Given** an authenticated user on the profile page, **When** they update their full name and click save, **Then** the change is persisted and reflected in the header and all pages without requiring re-signin.

3. **Given** an authenticated user on the profile page, **When** they update their password and click save, **Then** the new password is required for future signins.

4. **Given** an authenticated user updating their background information, **When** they click save, **Then** the personalization engine uses the updated background immediately for new recommendations.

---

### User Story 5 - Sign Out (Priority: P2)

An authenticated user can sign out from the application, invalidating their JWT token and returning to unauthenticated state.

**Why this priority**: Sign out is important for multi-user devices and security but not required for MVP. Default session expiry provides fallback protection.

**Independent Test**: Can be fully tested by signing in, clicking sign out, and verifying protected features are disabled afterwards.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing the header, **When** they click the "Sign Out" button, **Then** their JWT token is cleared from local storage and they are redirected to the home page.

2. **Given** a user who just signed out, **When** they attempt to access a protected feature, **Then** they see the "Sign in" prompt and cannot proceed.

---

### Edge Cases

- **What happens if a user signs up but the background questionnaire is partially incomplete?** → Require all questionnaire fields; show validation errors for missing fields before account creation.

- **What happens if an API call includes an expired JWT token?** → Return 401 Unauthorized; client-side detects and prompts user to re-signin.

- **What happens if a user's background information is very long or contains special characters?** → Validate and sanitize all questionnaire inputs; truncate if necessary (documentation required for limits).

- **What happens if password reset is requested?** → Password reset is out of scope for MVP. Users who forget their password must contact an administrator for reset. Future enhancement: implement email-based password reset flow.

- **What happens if a user tries to sign in from multiple devices/browsers simultaneously?** → System supports unlimited concurrent sessions. Users can be logged in on multiple devices (phone, laptop, browser tabs, etc.) simultaneously with independent JWT tokens for each session.

- **What happens if network connectivity is lost during signup?** → Client-side error handling should display "Network error. Please try again" and allow user to retry without data loss.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to create accounts with email, password, full name, and background questionnaire (software_background, hardware_background, ros_experience, python_level, learning_goal, available_hardware).

- **FR-002**: System MUST validate email format and uniqueness (no duplicate signups with same email).

- **FR-003**: System MUST validate password strength (minimum 8 characters, uppercase, lowercase, numbers).

- **FR-004**: System MUST hash passwords using Bcrypt before storage (never store plain text).

- **FR-005**: System MUST authenticate users via email/password and issue JWT tokens upon successful signin.

- **FR-006**: System MUST support JWT token expiry of 7 days by default and 30 days when "Remember me" is checked during signin.

- **FR-007**: System MUST use HS256 algorithm for JWT signing and verification.

- **FR-008**: System MUST provide GET endpoint to retrieve authenticated user's profile (email, name, background info).

- **FR-009**: System MUST provide PUT/PATCH endpoint to update authenticated user's profile (name, password, background info).

- **FR-010**: System MUST provide POST endpoint for user signout that invalidates JWT tokens.

- **FR-011**: System MUST persist all user and background data in Neon Postgres database.

- **FR-012**: System MUST protect /api/translate endpoint requiring valid JWT token in Authorization header.

- **FR-013**: System MUST protect /api/personalize endpoint requiring valid JWT token in Authorization header.

- **FR-014**: System MUST return 401 Unauthorized for requests to protected endpoints without valid JWT.

- **FR-015**: System MUST display "Sign in to translate" prompt on TranslationButton for unauthenticated users.

- **FR-016**: System MUST display "Sign in to personalize" prompt on PersonalizationButton for unauthenticated users.

- **FR-017**: System MUST display authenticated user's full name in header/user menu.

- **FR-018**: System MUST be fully responsive and functional on mobile devices (no layout breaks, touch-friendly buttons).

- **FR-019**: System MUST not display console errors (browser dev tools console must be clean).

- **FR-020**: System MUST enable CORS for localhost:3000 (frontend) and localhost:8080 (potential partner services).

- **FR-021**: System MUST automatically sign in new users immediately after successful signup.

- **FR-022**: System MUST validate all user inputs (no SQL injection, XSS, or other OWASP vulnerabilities).

### Key Entities

- **User**: Represents an authenticated user account. Attributes: id (unique identifier), email (unique, required), password_hash (Bcrypt hashed, required), full_name (required), created_at (timestamp), updated_at (timestamp).

- **UserBackground**: Represents the background questionnaire data for a user. Attributes: user_id (foreign key), software_background (text/enum), hardware_background (text/enum), ros_experience (level/years), python_level (beginner/intermediate/advanced/expert), learning_goal (text), available_hardware (text/list).

- **AuthToken**: Represents JWT token metadata and state. Attributes: token (JWT string), user_id (foreign key), expiry (timestamp), created_at (timestamp), revoked (boolean for signout support).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: New users can complete signup with background questionnaire and auto-signin in under 90 seconds.

- **SC-002**: Registered users can signin with valid credentials and receive JWT token in under 2 seconds.

- **SC-003**: Unauthenticated users see "Sign in to translate" and "Sign in to personalize" prompts without exceptions or console errors.

- **SC-004**: Authenticated users can click TranslationButton and PersonalizationButton without 401 errors when JWT is valid.

- **SC-005**: API endpoints (/api/translate, /api/personalize) return 401 Unauthorized when no JWT or expired JWT is provided.

- **SC-006**: Authenticated user's name appears in header within 1 second of signin.

- **SC-007**: Feature is fully responsive on mobile (viewport 320px+) with no layout breaks or unclickable buttons.

- **SC-008**: Browser console shows zero errors during signup, signin, feature usage, and signout flows.

- **SC-009**: RAG chatbot functionality remains unchanged and fully operational (no regressions).

- **SC-010**: JWT tokens with 7-day expiry persist across page refreshes and remain valid for 7 calendar days.

- **SC-011**: JWT tokens with 30-day expiry (remember_me) persist and remain valid for 30 calendar days.

- **SC-012**: Password updates require old password verification and invalidate all existing tokens immediately.

- **SC-013**: Profile updates reflect across the app without requiring page reload or re-signin.

---

## Assumptions

- **Authentication Library**: System uses a JWT-based authentication approach; better-auth library (or similar) handles token lifecycle on backend.

- **Token Storage**: Frontend stores JWT tokens in secure storage (HttpOnly cookies or sessionStorage with HTTPS).

- **Email Verification**: Email verification is not required for MVP (future enhancement); users can signin immediately after signup.

- **Password Reset**: Password reset via email is out of scope for MVP (users can update password via profile edit if they remember current password).

- **SSO/OAuth**: Social login (Google, GitHub, etc.) is out of scope; email/password only for MVP.

- **Rate Limiting**: Basic rate limiting (signup/signin) on backend to prevent brute force attacks (not detailed in this spec).

- **CORS Configuration**: FastAPI backend is configured to accept requests from localhost:3000 and localhost:8080.

- **Database Connection**: Neon Postgres connection string is already available in environment; no new database setup required.

- **Bcrypt Configuration**: Bcrypt salt rounds = 10 (industry standard).

- **JWT Secret**: HS256 secret is stored securely in backend environment variables (not hardcoded).

---

## Constraints

- **No Breaking Changes**: Must not break existing RAG chatbot functionality or any other features.

- **Existing Infrastructure**: Must use existing Neon Postgres database connection; no new infrastructure setup.

- **Frontend Stack**: Must work with Docusaurus (React-based) frontend; no major framework changes.

- **Backend Stack**: Must work with existing FastAPI backend; use compatible JWT/Bcrypt libraries.

- **Scope**: Limited to user authentication and feature protection; does not include complex authorization (roles, permissions).

- **Timeline**: Target ~4-6 hours for complete implementation (signup + signin + profile + protected endpoints + UI integration).

- **Frontend Components**: 5 components maximum (SignupPage, SigninPage, AuthProvider, ProtectedRoute, UserMenu).

- **Backend Endpoints**: 5 endpoints maximum (signup, signin, signout, get profile/me, update profile).

---

## Out of Scope

- Email verification (OTP, confirmation links)
- Password reset via email
- Social login (OAuth2, Google, GitHub)
- Two-factor authentication (2FA)
- Role-based access control (RBAC)
- Account deletion
- Audit logging
- Account lockout after failed attempts
- API key authentication
