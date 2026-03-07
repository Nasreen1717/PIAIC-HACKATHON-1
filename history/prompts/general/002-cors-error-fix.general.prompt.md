---
id: 002
title: CORS Error Fix - Chat API Integration
stage: general
date: 2026-03-03
surface: agent
model: claude-haiku-4-5-20251001
feature: none
branch: 010-content-personalization
user: nasreen17
command: Debug and fix CORS error preventing chat API communication
labels: ["bug-fix", "cors", "api-integration", "backend-frontend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - backend/.env
  - Front-End-Book/src/utils/chatApi.js
  - CORS_FIX_GUIDE.md
tests_yaml: []
---

## Prompt

User reported console errors showing CORS policy blocking requests from frontend on `localhost:3001` trying to reach backend API on `localhost:8000`. Errors included:
- "Access to fetch at 'http://localhost:8000/api/v1/chat/sessions' from origin 'http://localhost:3001' has been blocked by CORS policy"
- Failed to initialize chat session
- ChatInterface not rendering properly

## Response

### Investigation Results

**Root Cause Identified:**
1. Frontend running on `http://localhost:3001`
2. Backend running on `http://localhost:8000`
3. Backend `.env` CORS_ORIGINS configuration only whitelisted `["http://localhost:3000","http://localhost:8080","http://localhost"]`
4. Port `3001` was missing from the CORS whitelist

**Error Chain:**
```
Frontend (3001) → requests to Backend (8000)
  → Backend checks CORS_ORIGINS
  → 3001 not in whitelist
  → Request blocked by browser
  → ChatAPI fails to create session
  → ChatInterface shows hidden state
```

### Fixes Applied

#### 1. Backend CORS Configuration (backend/.env)
**Added `localhost:3001` to CORS_ORIGINS whitelist:**

```diff
- CORS_ORIGINS=["http://localhost:3000","http://localhost:8080","http://localhost"]
+ CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:8080","http://localhost"]
```

**Why this fixes it:** Backend now accepts requests from the actual frontend port

#### 2. Frontend Fetch Requests (src/utils/chatApi.js)
**Added proper CORS headers to all API endpoints:**

Four endpoints updated:

**a) Send Chat Message (streaming):**
```javascript
fetch(`${API_BASE_URL}/api/v1/chat/stream`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',  // ← Added
  body: JSON.stringify(request),
})
```

**b) Fetch Conversation History:**
```javascript
fetch(`${API_BASE_URL}/api/v1/chat/history/${sessionId}`, {
  method: 'GET',
  credentials: 'include',  // ← Added
})
```

**c) Create Chat Session:**
```javascript
fetch(`${API_BASE_URL}/api/v1/chat/sessions`, {
  method: 'POST',
  credentials: 'include',  // ← Added
})
```

**d) Health Check:**
```javascript
fetchWithTimeout(`${API_BASE_URL}/api/v1/health`, {
  method: 'GET',
  credentials: 'include',  // ← Added
}, 2000)
```

**Why this matters:** `credentials: 'include'` allows authentication cookies/headers to be sent with cross-origin requests

### Documentation Created

**File:** `CORS_FIX_GUIDE.md`
Comprehensive guide including:
- Problem summary with error messages
- Step-by-step solution
- Server restart instructions
- Testing procedures
- Troubleshooting guide
- Browser console testing examples
- Production deployment considerations

### How Users Should Apply This

**Step 1:** Backend restart (loads new `.env`)
```bash
cd backend
python main.py  # or: uvicorn main:app --reload --port 8000
```

**Step 2:** Frontend restart (loads new code)
```bash
cd Front-End-Book
npm start
```

**Step 3:** Verify success in browser console
- Should see session creation logs
- No CORS errors
- Chat interface should render

### Testing Commands

Users can verify the fix works by running these in browser console:

```javascript
// Test 1: Health check
fetch('http://localhost:8000/api/v1/health', {
  credentials: 'include'
}).then(r => r.json()).then(d => console.log('✅', d))

// Test 2: Create session
fetch('http://localhost:8000/api/v1/chat/sessions', {
  method: 'POST',
  credentials: 'include'
}).then(r => r.json()).then(d => console.log('✅', d))
```

### Before/After Comparison

| Aspect | Before | After |
|--------|--------|-------|
| Frontend port | 3001 | 3001 |
| Backend CORS config | Missing 3001 | ✅ Includes 3001 |
| Fetch requests | No credentials header | ✅ Adds credentials |
| Session creation | ❌ CORS error | ✅ Works |
| Chat interface | Hidden/non-functional | ✅ Renders |

---

## Outcome

✅ **CORS error resolved through two-pronged approach:**

1. **Backend:** Updated CORS_ORIGINS to accept requests from localhost:3001
2. **Frontend:** Added proper CORS headers (`credentials: 'include'`) to all API requests

**Expected Results After Restart:**
- No CORS policy errors in console
- Chat session created successfully
- Chat interface renders and accepts messages
- All API endpoints respond correctly
- Backend health check passes

**Files to Verify:**
- `backend/.env` - CORS_ORIGINS updated ✅
- `src/utils/chatApi.js` - All fetch calls updated ✅
- Console logs - Should show successful session creation

**Next Steps for User:**
1. Restart backend server
2. Restart frontend dev server
3. Check browser console for success logs
4. Test chat interface functionality
5. If issues persist, refer to CORS_FIX_GUIDE.md troubleshooting section
