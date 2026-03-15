# Quick Start: Translation Protection with Authentication

**Created**: 2026-02-10
**Feature**: Translation Protection with Authentication
**Target Audience**: Developers implementing the feature

---

## Overview

This guide walks through integrating JWT authentication protection into the translation feature. The feature restricts translation to authenticated users only, with clear UX messaging for logged-out users.

**Key Points**:
- Frontend protection already in place via ProtectedFeature wrapper
- Backend needs JWT validation dependency added to endpoint
- No new dependencies required
- Follows existing FastAPI auth patterns

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Docusaurus)                    │
│                                                                   │
│  Article Page                                                    │
│  ├─ TranslationButton component                                  │
│  │  └─ ProtectedFeature wrapper                                  │
│  │     ├─ if user != null: show "Translate to Urdu" button       │
│  │     └─ if user == null: show "Sign in to translate" prompt    │
│  │        └─ Link to /signin                                     │
│  └─ useTranslation hook                                          │
│     └─ Sends POST /api/v1/translate with Authorization header    │
│                                                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Request
                             │ Authorization: Bearer {token}
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                            │
│                                                                   │
│  POST /api/v1/translate                                          │
│  ├─ get_current_user dependency (from auth.py)                   │
│  │  ├─ Extract token from Authorization header                   │
│  │  ├─ Validate JWT signature & expiration                       │
│  │  ├─ Look up user in database                                  │
│  │  └─ Return User object (or raise 401 if invalid)              │
│  ├─ Perform translation (if user authenticated)                  │
│  └─ Return TranslateResponse (200) or error (401/400/503)        │
│                                                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Response
                             ├─ 200: {translated_text, confidence}
                             ├─ 401: {detail: "Invalid or expired token"}
                             ├─ 400: {detail: "Text too long..."}
                             └─ 503: {detail: "Service unavailable"}
```

---

## Frontend Setup

### 1. Verify ProtectedFeature Wrapper (Already Done)

**File**: `src/components/TranslationButton/index.tsx`

The component already uses ProtectedFeature. Verify this is in place:

```typescript
import { ProtectedFeature } from '@site/src/components/Auth/ProtectedFeature';

export default function TranslationButton(): JSX.Element {
  const { language, isLoading, error, toggleLanguage, clearError } = useTranslation();

  return (
    <ProtectedFeature featureName="Article translation">
      <div className={styles.container}>
        <button {...}>
          {isLoading ? 'Translating...' : 'Translate to Urdu 🌐'}
        </button>
        {/* error display, etc */}
      </div>
    </ProtectedFeature>
  );
}
```

**What this does**:
- ✅ Shows button only to logged-in users (checks `user` from useAuth)
- ✅ Shows "Article translation requires authentication" prompt to logged-out users
- ✅ Provides links to /signin and /signup

### 2. Verify useTranslation Hook Sends Token

**File**: `src/components/TranslationButton/useTranslation.ts`

Verify the hook includes Authorization header in fetch request:

```typescript
import { useAuth } from '@site/src/hooks/useAuth';

export default function useTranslation() {
  const { user, token } = useAuth();  // ← Get token from context
  const [language, setLanguage] = useState<'en' | 'ur'>('en');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<TranslationError | null>(null);

  const toggleLanguage = async () => {
    if (!token) {
      setError({ message: "Not authenticated", retryable: false });
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`  // ← Add token to header
        },
        body: JSON.stringify({
          text: getCurrentArticleText(),
          target_lang: 'ur'
        })
      });

      if (!response.ok) {
        // Handle error response
        const data = await response.json();

        // Handle 401: token expired or invalid
        if (response.status === 401) {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
          setError({
            message: "Session expired. Please sign in again.",
            retryable: false
          });
          // Optionally dispatch 'auth-changed' event to trigger AuthContext update
          window.dispatchEvent(new Event('storage'));
          return;
        }

        // Handle other errors
        setError({
          message: data.detail || 'Translation failed',
          retryable: response.status >= 500  // Retry for 5xx errors
        });
        return;
      }

      const result = await response.json();
      setLanguage(language === 'en' ? 'ur' : 'en');
      // Update article content with result.translated_text
    } catch (err) {
      setError({
        message: 'Network error. Check your connection.',
        retryable: true
      });
    } finally {
      setIsLoading(false);
    }
  };

  return { language, isLoading, error, toggleLanguage, clearError };
}
```

**Key points**:
- ✅ Get `token` from useAuth hook
- ✅ Include in Authorization header as `Bearer {token}`
- ✅ Handle 401 response: clear localStorage, show login prompt
- ✅ Handle 400/503 responses: show appropriate error messages

### 3. Test Frontend Locally

1. Start Docusaurus dev server:
   ```bash
   cd /mnt/d/code/Hackathon-1/Front-End-Book
   npm run start
   ```

2. Open browser to http://localhost:3000/docs/any-page

3. Test logged-out state:
   - Clear localStorage: `localStorage.clear()`
   - Refresh page
   - Should see "Article translation requires authentication" prompt
   - Clicking "Sign In to Continue" should navigate to /signin

4. Test logged-in state:
   - Sign in at /signin
   - Navigate back to article page
   - Should see "Translate to Urdu 🌐" button
   - Clicking should show "Translating..." spinner (until backend responds)

---

## Backend Setup

### 1. Create Translation Endpoint

**File**: `backend/app/api/v1/translate.py` (NEW)

Create this file with the following content:

```python
"""
Translation API endpoints.

Provides POST /api/v1/translate endpoint for translating article content.
Requires JWT authentication via Authorization header.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.models import User
from app.routes.auth import get_current_user, get_db
from app.schemas.translate import TranslateRequest, TranslateResponse
# TODO: Import translation service (may already exist)
# from app.services.translation import translation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/translate", tags=["translate"])


@router.post("/", response_model=TranslateResponse)
async def translate(
    request: TranslateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TranslateResponse:
    """
    Translate article content to target language.

    Requires valid JWT authentication token in Authorization header.

    Args:
        request: TranslateRequest with text to translate
        current_user: Authenticated user (guaranteed by get_current_user dependency)
        db: Database session (for potential future user tracking)

    Returns:
        TranslateResponse with translated text, language detection, and confidence

    Raises:
        HTTPException: 400 for invalid input, 401 for unauthenticated, 503 for service error
    """
    try:
        # Validate input
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )

        if len(request.text) > 50000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text too long (max 50000 chars)"
            )

        logger.info(f"Translation request from user {current_user.email}: {len(request.text)} chars to {request.target_lang}")

        # TODO: Call translation service
        # result = await translation_service.translate(
        #     text=request.text,
        #     source_lang=request.source_lang,
        #     target_lang=request.target_lang
        # )

        # Placeholder response (replace with actual translation service call)
        return TranslateResponse(
            translated_text="[Translation would appear here]",
            detected_lang=request.source_lang,
            confidence=1.0,
            session_id=request.session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Translation service unavailable"
        )
```

### 2. Create Translation Schemas

**File**: `backend/app/schemas/translate.py` (NEW)

```python
"""Schemas for translation API."""

from pydantic import BaseModel, Field
from typing import Optional


class TranslateRequest(BaseModel):
    """Request to translate text."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Text to translate"
    )
    source_lang: str = Field(
        default="en",
        description="Source language code (ISO 639-1)"
    )
    target_lang: str = Field(
        default="ur",
        description="Target language code (only 'ur' supported)"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session identifier"
    )


class TranslateResponse(BaseModel):
    """Response from translation endpoint."""

    translated_text: str = Field(
        ...,
        description="Translated text"
    )
    detected_lang: str = Field(
        ...,
        description="Language detected in source"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0)"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Echo back of request session_id"
    )
```

### 3. Register Router in main.py

**File**: `backend/app/main.py`

Add import and include router:

```python
# At the top with other imports
from app.api.v1 import chat, debug, translate  # ← Add translate

# In the section with include_router calls
app.include_router(health.router)
app.include_router(auth_router)
app.include_router(chat.router)
app.include_router(translate.router)  # ← Add this line
app.include_router(debug.router)
```

### 4. Test Backend Locally

1. Start backend server:
   ```bash
   cd /mnt/d/code/Hackathon-1/backend
   python -m uvicorn app.main:app --reload
   ```

2. Test without authentication (should fail):
   ```bash
   curl -X POST http://localhost:8000/api/v1/translate \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello world"}'

   # Expected response:
   # 401 Unauthorized
   # {"detail": "Not authenticated"}
   ```

3. Test with valid token (sign in first, copy token, then request):
   ```bash
   # 1. Sign in to get token
   curl -X POST http://localhost:8000/api/auth/signin \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123"}'

   # Copy the returned access_token

   # 2. Use token in translation request
   curl -X POST http://localhost:8000/api/v1/translate \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer {access_token}" \
     -d '{"text": "The quick brown fox"}'

   # Expected response:
   # 200 OK
   # {"translated_text": "[Translation]", "detected_lang": "en", "confidence": 1.0}
   ```

4. Test with invalid token (should fail):
   ```bash
   curl -X POST http://localhost:8000/api/v1/translate \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer invalid_token_here" \
     -d '{"text": "Hello world"}'

   # Expected response:
   # 401 Unauthorized
   # {"detail": "Invalid or expired token"}
   ```

---

## Integration Testing

### Frontend + Backend Together

1. Start both servers (frontend on 3000, backend on 8000)

2. Test logged-out user:
   - Clear auth from localStorage: `localStorage.clear()`
   - Refresh article page
   - Verify "Sign in to translate" prompt displays
   - Click "Sign In to Continue", sign in, return to article
   - Verify button now shows "Translate to Urdu 🌐"

3. Test translation flow:
   - Click "Translate to Urdu 🌐" button
   - Verify "Translating..." spinner displays
   - Wait for response
   - Verify article text updates to Urdu (or error displays)

4. Test token expiration:
   - Modify token in localStorage to invalid value: `localStorage.setItem('auth_token', 'invalid')`
   - Click translate button
   - Should show 401 error
   - Auth state should clear (prompt reappears)

---

## Security Checklist

- ✅ Frontend hides button from logged-out users (ProtectedFeature)
- ✅ Frontend sends token in Authorization header (useTranslation)
- ✅ Backend validates token on every request (get_current_user dependency)
- ✅ Backend rejects 401 if token missing or invalid
- ✅ Error messages don't expose token details
- ✅ Token stored in localStorage (standard for web apps)
- ✅ CORS allows Authorization header (verify in main.py CORS config)
- ✅ No hardcoded tokens in code

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| "Not authenticated" on valid token | CORS not allowing Authorization header | Check `allow_headers=["*"]` in CORSMiddleware |
| Button missing on article page | ProtectedFeature not imported | Verify import in TranslationButton/index.tsx |
| 401 even with valid token | Token format wrong | Ensure useTranslation sends `Bearer {token}` |
| Spinner spins forever | Backend endpoint doesn't exist | Verify router registered in main.py |
| No error message on 401 | useTranslation not handling error | Check error handling code in useTranslation hook |

---

## File Checklist

Use this to verify all required files are in place:

**Backend**:
- [ ] `backend/app/api/v1/translate.py` created with POST /translate endpoint
- [ ] `backend/app/schemas/translate.py` created with TranslateRequest/Response
- [ ] `backend/app/main.py` updated to include translate router
- [ ] `get_current_user` dependency correctly applied to endpoint

**Frontend**:
- [ ] `src/components/TranslationButton/index.tsx` uses ProtectedFeature wrapper
- [ ] `src/components/TranslationButton/useTranslation.ts` sends Authorization header
- [ ] Error handling includes 401 response detection
- [ ] Token cleared from localStorage on 401 response

**Testing**:
- [ ] Backend responds 401 without token
- [ ] Backend responds 401 with invalid token
- [ ] Backend responds 200 with valid token
- [ ] Frontend shows prompt to logged-out users
- [ ] Frontend shows button to logged-in users
- [ ] Frontend handles 401 by clearing auth state

---

## Next Steps

1. Complete the implementation using this guide
2. Run integration tests to verify flows
3. Create unit and E2E tests
4. Run `/sp.tasks` to generate detailed task list
5. Commit changes with comprehensive test coverage

---

## References

- **OpenAPI Contract**: `contracts/translate-api.openapi.json`
- **Data Model**: `data-model.md`
- **Existing Auth Pattern**: `backend/app/routes/auth.py`
- **Existing JWT Utils**: `backend/app/security.py`
- **Existing ProtectedFeature**: `src/components/Auth/ProtectedFeature.tsx`

---

**Last Updated**: 2026-02-10
**Status**: Ready for Implementation
