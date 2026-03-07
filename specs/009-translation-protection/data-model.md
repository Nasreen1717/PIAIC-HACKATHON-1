# Data Model: Translation Protection with Authentication

**Created**: 2026-02-10
**Feature**: Translation Protection with Authentication
**Status**: Phase 1 Design Output

---

## Entity Models

### 1. User (Existing Entity - No Changes)

**Source**: `backend/app/db/models.py`

**Purpose**: Represents authenticated user making translation requests

**Fields**:
| Field | Type | Validation | Notes |
|-------|------|-----------|-------|
| id | Integer (PK) | Not null, auto-increment | Primary key |
| email | String | Not null, unique | Used in JWT "sub" claim |
| full_name | String | Optional | Display name |
| is_active | Boolean | Not null, default=True | Deactivated users rejected |
| created_at | DateTime | Not null, auto-timestamp | Account creation time |
| password_hash | String | Not null | Not transmitted to frontend |
| background | Foreign Key (UserBackground) | Optional | User survey data |

**State Transitions**:
- Active → Inactive: User deactivated (edge case handling)
- Active → Token Expired: Token validation fails; user re-authenticates

**Usage in Translation Feature**:
- Passed by `get_current_user()` dependency after token validation
- Guarantees user is authenticated and active
- Email extracted from JWT "sub" claim for DB lookup

**No Changes Required**: This entity is unchanged; already exists and is properly secured.

---

### 2. TranslationRequest (New DTO)

**Source**: `backend/app/schemas/translate.py` (to be created)

**Purpose**: Represents user request to translate content

**Fields**:
| Field | Type | Validation | Notes |
|-------|------|-----------|-------|
| text | String | Not empty, ≤50k chars | Content to translate |
| source_lang | String | Default="en" | Language code (ISO 639-1) |
| target_lang | String | Default="ur" | Always "ur" for this feature |
| session_id | String (UUID) | Optional | For tracking translation session |

**Validation Rules**:
```python
class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    source_lang: str = "en"
    target_lang: str = "ur"
    session_id: Optional[str] = None

    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be only whitespace')
        return v.strip()
```

**JSON Example**:
```json
{
  "text": "The quick brown fox jumps over the lazy dog.",
  "source_lang": "en",
  "target_lang": "ur",
  "session_id": "session_abc123"
}
```

---

### 3. TranslationResponse (New DTO)

**Source**: `backend/app/schemas/translate.py` (to be created)

**Purpose**: Represents successful translation result

**Fields**:
| Field | Type | Notes |
|-------|------|-------|
| translated_text | String | Urdu translation of input |
| detected_lang | String | Language detected in source text |
| confidence | Float (0.0-1.0) | Confidence in translation quality |
| session_id | String | Echo back session_id for tracking |

**Validation Rules**:
```python
class TranslateResponse(BaseModel):
    translated_text: str = Field(..., min_length=1)
    detected_lang: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    session_id: Optional[str] = None
```

**JSON Example**:
```json
{
  "translated_text": "تیز رفتار بھوری لومڑی سست کتے کے اوپر کودتی ہے۔",
  "detected_lang": "en",
  "confidence": 0.95,
  "session_id": "session_abc123"
}
```

---

### 4. ErrorResponse (Reused from Existing Pattern)

**Source**: FastAPI HTTPException (implicit in error responses)

**Purpose**: Represents error state for failed translation requests

**Status Codes & Messages**:

| Status | Error Message | Meaning | Frontend Action |
|--------|---------------|---------|-----------------|
| 401 | "Not authenticated" | Authorization header missing | Show login prompt |
| 401 | "Invalid or expired token" | Token validation failed | Clear auth state, show login |
| 400 | "Text cannot be empty" | Validation failed | Show error, allow retry |
| 400 | "Text too long (max 50000 chars)" | Input exceeds limit | Truncate text, allow retry |
| 503 | "Translation service unavailable" | Backend service error | Show error, suggest retry |

**JSON Example (401)**:
```json
{
  "detail": "Invalid or expired token"
}
```

**JSON Example (400)**:
```json
{
  "detail": "Text too long (max 50000 chars)"
}
```

---

## API State Flow

### Happy Path: Authenticated Translation

```
User (logged in)
    ↓
TranslationButton visible (ProtectedFeature checks user != null)
    ↓
User clicks button
    ↓
Frontend fetches: POST /api/v1/translate
  Headers: { Authorization: "Bearer {token}", Content-Type: "application/json" }
  Body: { text: "...", source_lang: "en", target_lang: "ur" }
    ↓
Backend get_current_user dependency:
  1. Extracts token from Authorization header ✅
  2. Validates token with extract_email_from_token() ✅
  3. Looks up user in DB by email ✅
  4. Returns User object (guaranteed active) ✅
    ↓
Endpoint receives:
  - request: TranslateRequest (validated)
  - current_user: User (authenticated)
    ↓
Translation service processes text
    ↓
Response: TranslateResponse (200 OK)
    ↓
Frontend receives result, updates UI with translated text
```

### Error Path: Unauthenticated Request

```
User (logged out)
    ↓
TranslationButton hidden (ProtectedFeature checks user == null)
    ↓
Login prompt shows ("Article translation requires authentication")
    ↓
[Alternative: developer tries direct API call without token]
    ↓
Frontend attempts: POST /api/v1/translate
  Headers: { Content-Type: "application/json" }  ← No Authorization header
  Body: { text: "..." }
    ↓
Backend get_current_user dependency:
  1. Checks Authorization header → NOT FOUND ❌
  2. Raises HTTPException(401, "Not authenticated")
    ↓
Response: 401 Unauthorized { detail: "Not authenticated" }
    ↓
Frontend catch: response.status === 401
    ↓
Clear auth state (localStorage.removeItem 'auth_token', 'auth_user')
    ↓
Show login prompt
```

### Error Path: Token Expired

```
User (logged in, but token expired)
    ↓
TranslationButton visible (ProtectedFeature checks cached user state)
    ↓
User clicks button
    ↓
Frontend fetches: POST /api/v1/translate
  Headers: { Authorization: "Bearer {expired_token}", ... }
    ↓
Backend get_current_user dependency:
  1. Extracts token ✅
  2. Calls extract_email_from_token(token) → returns None (JWT expired) ❌
  3. Raises HTTPException(401, "Invalid or expired token")
    ↓
Response: 401 Unauthorized { detail: "Invalid or expired token" }
    ↓
Frontend catch: response.status === 401
    ↓
Clear auth state
    ↓
Show login prompt ("Session expired. Please sign in again.")
```

---

## Frontend State Management

### AuthContext State (Existing)

**Source**: `src/context/AuthContext.tsx`

**Relevant State**:
```typescript
interface AuthContextType {
  user: User | null;           // User object or null if logged out
  token: string | null;        // JWT token or null
  isLoading: boolean;          // Signin/signup in progress
  error: string | null;        // Auth error message
  signin: () => Promise<void>; // Signin method
  signout: () => Promise<void>; // Signout method
}
```

**Local Storage Keys**:
- `auth_token`: JWT token string
- `auth_user`: Serialized User object (JSON)

**Flow**:
1. User signs in → AuthContext stores `token` and `user`
2. Token sent in Authorization header for API requests
3. Token expires → Backend returns 401 → Frontend clears token from localStorage
4. AuthContext detects change (via storage event) → Re-renders ProtectedFeature
5. ProtectedFeature sees `user == null` → Shows login prompt

### useTranslation Hook State (Existing)

**Source**: `src/components/TranslationButton/useTranslation.ts`

**State**:
```typescript
const [language, setLanguage] = useState<'en' | 'ur'>('en');
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<TranslationError | null>(null);
```

**Error Type**:
```typescript
interface TranslationError {
  message: string;
  retryable: boolean;  // true if user can retry
}
```

**Flow**:
1. User clicks translation button
2. Hook calls `/api/v1/translate` with current article text
3. Includes Authorization header with token from AuthContext
4. If response.status === 401:
   - Clear localStorage auth data
   - Dispatch 'auth-changed' event
   - Show error: "Session expired. Please sign in again."
5. If response.status === 200:
   - Update language state
   - Display translated text
6. If response.status >= 500:
   - Set error.retryable = true
   - Show error with Retry button

---

## Database Constraints (No New Tables)

✅ No new tables required
✅ Existing `users` table already has all needed fields
✅ Existing indexes on `users.email`, `users.id` support lookups
✅ No schema migrations needed

---

## Security Considerations

### Data Sensitivity

| Field | Sensitive? | Protection |
|-------|-----------|-----------|
| JWT Token | YES | Transmitted only in Authorization header; not in URLs; httpOnly not required (OAuth pattern) |
| User Email | LOW | Used only for token validation; not returned in translation response |
| User ID | LOW | Not exposed in error messages; only used internally |
| Translated Text | NO | User-provided content; no PII should be in it |

### Protection Layers

1. **Frontend**: ProtectedFeature component hides button from logged-out users
2. **API**: get_current_user dependency validates token on every request
3. **Token Validation**: extract_email_from_token() checks JWT signature and expiration
4. **DB Lookup**: Verifies user exists and is active
5. **Error Handling**: No sensitive info (token details) in error messages

---

## Validation Rules Summary

| Entity | Field | Rule | Why |
|--------|-------|------|-----|
| TranslateRequest | text | Not empty, ≤50k chars | Prevent DoS; reasonable limit for translation service |
| TranslateRequest | source_lang | ISO 639-1 code | Standard language code format |
| TranslateRequest | target_lang | Must be "ur" | Only Urdu supported in this feature |
| User | email | Must match token "sub" | Prevent token spoofing |
| User | is_active | Must be True | Deactivated users cannot translate |

---

## Testing Scenarios

### Unit Tests (Data Validation)

- ✅ TranslateRequest with empty text → ValidationError
- ✅ TranslateRequest with >50k chars → ValidationError
- ✅ TranslateRequest with invalid language code → ValidationError
- ✅ TranslateResponse fields serialized correctly → JSON valid

### Integration Tests (State Transitions)

- ✅ Authenticated user makes request → Returns 200 with TranslateResponse
- ✅ Unauthenticated user makes request → Returns 401 with error detail
- ✅ Expired token sends request → Returns 401
- ✅ Active user deactivated → Returns 401 on next request
- ✅ 401 response clears frontend auth state → ProtectedFeature re-renders

---

## Schema Diagram

```
┌─────────────────────────┐
│      Frontend           │
├─────────────────────────┤
│ AuthContext             │
│  - user: User | null    │
│  - token: string | null │
│  - isLoading: bool      │
│  - error: string | null │
└────────┬────────────────┘
         │
         │ (fetch + Authorization header)
         ↓
┌─────────────────────────┐
│   API: /api/v1/translate│
├─────────────────────────┤
│ POST /translate         │
│  Request: TranslateReq  │
│  Response: TranslateResp│
└────────┬────────────────┘
         │
         │ (get_current_user dependency)
         ↓
┌─────────────────────────┐
│   Database              │
├─────────────────────────┤
│ users table             │
│  - id: int              │
│  - email: string        │
│  - is_active: bool      │
│  - ...                  │
└─────────────────────────┘
```

---

## Conclusion

The data model is simple and leverages existing infrastructure:
- **No new database tables**
- **Two new DTOs** (TranslateRequest, TranslateResponse)
- **One new endpoint** (POST /api/v1/translate)
- **One reused dependency** (get_current_user from auth.py)
- **Existing auth state management** (AuthContext, useAuth hook)

All validation rules, state transitions, and security layers are documented above and ready for implementation.
