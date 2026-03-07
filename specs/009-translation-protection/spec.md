# Feature Specification: Translation Protection with Authentication

**Feature Branch**: `009-translation-protection`
**Created**: 2026-02-10
**Status**: Draft
**Input**: User description: "Add authentication protection to the existing TranslationButton component in the Docusaurus-based Physical AI textbook. Currently, the translation feature works but is accessible to everyone. We need to restrict it to logged-in users only."

## Overview

The Translation feature currently allows any visitor to translate article content to Urdu without authentication. This spec defines the protection of the translation feature by requiring user authentication, with clear UX for logged-out users while maintaining existing functionality for authenticated users.

## User Scenarios & Testing

### User Story 1 - Logged-in User Translates Article (Priority: P1)

A logged-in user visits an article and wants to read it in Urdu. They see the translation button available and can use it immediately.

**Why this priority**: Core value - the primary use case that shows the feature working for authenticated users.

**Independent Test**: Can be fully tested by authenticating a user, visiting an article page, clicking the translation button, and verifying the translation loads successfully.

**Acceptance Scenarios**:

1. **Given** user is logged in, **When** user visits an article page, **Then** translation button displays and is enabled
2. **Given** user is logged in and views article in English, **When** user clicks "Translate to Urdu 🌐" button, **Then** article content translates to Urdu and button changes to "Back to English 🌐"
3. **Given** article is in Urdu, **When** user clicks "Back to English 🌐" button, **Then** article reverts to English
4. **Given** translation is in progress, **When** user views the button, **Then** loading spinner displays with "Translating..." text
5. **Given** translation fails (network error), **When** user sees error message, **Then** error dismisses automatically after 5 seconds or user can click retry

---

### User Story 2 - Logged-out User Sees Sign-In Prompt (Priority: P1)

A logged-out user visits an article and sees a clear message indicating they need to sign in to use the translation feature, with convenient links to sign in or sign up.

**Why this priority**: Core security requirement - blocks unauthorized access and guides users to authentication.

**Independent Test**: Can be fully tested by visiting an article page while logged out and verifying the authentication prompt displays correctly.

**Acceptance Scenarios**:

1. **Given** user is logged out, **When** user visits an article page, **Then** translation button area is replaced with authentication prompt
2. **Given** user is logged out and sees authentication prompt, **When** user reads the message, **Then** message states "Article translation requires authentication"
3. **Given** authentication prompt is visible, **When** user clicks "Sign In to Continue" link, **Then** user is navigated to /signin page
4. **Given** authentication prompt is visible, **When** user sees signup prompt, **Then** prompt includes link to /signup page with text "Don't have an account? Sign up"
5. **Given** user signs in successfully, **When** user returns to article page, **Then** translation button is available and enabled

---

### User Story 3 - Backend Rejects Unauthorized Requests (Priority: P1)

The backend API validates incoming translation requests and rejects any request that lacks a valid authentication token.

**Why this priority**: Security requirement - prevents unauthorized translation requests even if frontend protection is bypassed.

**Independent Test**: Can be fully tested by making direct API calls to /api/translate without a token and verifying 401 response.

**Acceptance Scenarios**:

1. **Given** user makes API request without authentication token, **When** request reaches /api/translate endpoint, **Then** server responds with HTTP 401 Unauthorized
2. **Given** user makes API request with invalid/expired token, **When** request reaches /api/translate endpoint, **Then** server responds with HTTP 401 Unauthorized with clear error message
3. **Given** user makes API request with valid token, **When** request reaches /api/translate endpoint, **Then** request is processed normally and translation is performed
4. **Given** backend receives translation request, **When** token validation middleware runs, **Then** request context includes authenticated user information

---

### User Story 4 - Mobile Responsive Design (Priority: P2)

Translation button and authentication prompt are responsive and render correctly on mobile, tablet, and desktop devices.

**Why this priority**: Ensures feature works across all device types and maintains usability on mobile.

**Independent Test**: Can be fully tested by viewing article on mobile/tablet/desktop and verifying layout and functionality.

**Acceptance Scenarios**:

1. **Given** user views article on mobile device, **When** page loads, **Then** translation button/prompt displays with appropriate spacing
2. **Given** user is on mobile and sees error message, **When** error displays, **Then** error container is readable and action buttons are tap-friendly
3. **Given** user is on desktop, **When** user hovers over translation button, **Then** hover state displays correctly

---

### Edge Cases

- What happens if user's session expires while translation is in progress?
- How does the system handle the case where frontend protection is disabled (e.g., via browser dev tools)?
- What if the user signs out from another tab while viewing an article?
- How does the feature behave if the backend /api/translate endpoint is temporarily unavailable?
- What happens if a previously authenticated user's token becomes invalid?

## Requirements

### Functional Requirements

- **FR-001**: Frontend MUST display translation button only to authenticated users (checked via useAuth hook)
- **FR-002**: Frontend MUST display "Sign in to translate" message with authentication links to logged-out users
- **FR-003**: Frontend MUST include "Article translation" as featureName in ProtectedFeature component to show appropriate messaging
- **FR-004**: Translation button MUST maintain existing functionality (toggle between English and Urdu) for authenticated users
- **FR-005**: Backend /api/translate endpoint MUST validate JWT token from Authorization header
- **FR-006**: Backend MUST reject requests without valid token with HTTP 401 Unauthorized response
- **FR-007**: Backend MUST include clear error message in 401 response explaining authentication requirement
- **FR-008**: Frontend MUST display loading state ("Translating..." text + spinner) while API request is in progress
- **FR-009**: Frontend MUST display error messages when translation fails and allow retry attempt
- **FR-010**: Frontend MUST auto-dismiss error messages after 5 seconds
- **FR-011**: Authentication state changes in other tabs/windows MUST be reflected in current page (via storage events or auth-changed event)

### Key Entities

- **User**: Authenticated user making translation requests (from existing AuthContext)
  - Has JWT token (stored in auth_token localStorage)
  - Is identified by email and user ID

- **Translation Request**: API request to translate article content
  - Includes article content and target language (Urdu)
  - Must include JWT token in Authorization header
  - Returns translated content on success, error message on failure

- **Authentication Session**: User's logged-in state
  - Stored in localStorage (auth_token, auth_user)
  - Can change across browser tabs/windows
  - Can expire if token becomes invalid

## Success Criteria

### Measurable Outcomes

- **SC-001**: Logged-out users see authentication prompt instead of translation button (100% of logged-out users)
- **SC-002**: Logged-in users can successfully translate articles (100% of authenticated requests succeed when token is valid)
- **SC-003**: Unauthorized API requests are rejected with 401 status (100% of unauthenticated requests to /api/translate)
- **SC-004**: Translation feature maintains existing translation quality and speed (no performance degradation vs. unprotected version)
- **SC-005**: Zero console errors related to authentication or translation flow
- **SC-006**: Mobile responsive layout displays correctly on screens 320px and wider
- **SC-007**: User experience is consistent between logged-in and logged-out states with clear messaging

## Assumptions

1. **Existing Auth System**: The existing AuthContext from `src/context/AuthContext.tsx` correctly manages authentication state and tokens
2. **ProtectedFeature Component**: The `ProtectedFeature` component from `src/components/Auth/ProtectedFeature.tsx` is the appropriate pattern for feature-level protection
3. **Backend Readiness**: The FastAPI backend at /api/translate endpoint exists and can be modified to add JWT validation middleware
4. **JWT Tokens**: Tokens are stored in localStorage under `auth_token` key and follow standard JWT format with Bearer authentication scheme
5. **Hot Reload**: Docusaurus dev server hot reload will work correctly with auth state changes
6. **No Additional Auth Methods**: Feature uses existing email/password authentication, no OAuth or SSO integration needed
7. **Translation API**: Backend translation endpoint already handles language detection and translation logic, only needs token validation added

## Constraints

- Must not break existing translation functionality for authenticated users
- Must use existing AuthContext (no new auth system)
- Must maintain Docusaurus styling/theme consistency
- Must work with Docusaurus hot reload during development
- Frontend protection is for UX guidance; backend protection is enforced (defense in depth)
- TranslationButton already uses ProtectedFeature wrapper (no major refactoring needed)

## Out of Scope

- Translation quality improvements
- Additional language support beyond Urdu
- Translation caching or performance optimization
- Rate limiting on translation requests
- User-specific translation history or preferences
- Analytics on translation usage
- Internationalization of authentication prompts (UI stays in English)

## Dependencies

- Existing `useAuth` hook for accessing authentication state
- Existing `ProtectedFeature` component for conditional rendering
- Existing `AuthContext` providing user and token state
- Backend `/api/translate` endpoint for translation service
- FastAPI authentication middleware for JWT validation

## Notes

- Current implementation already wraps TranslationButton in ProtectedFeature, so most frontend work is complete
- Focus is primarily on ensuring backend validates tokens and frontend properly uses auth state
- Backend protection is critical since frontend can be bypassed; defense-in-depth approach needed
