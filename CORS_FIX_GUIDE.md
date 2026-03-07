# CORS Error Fix - Chat API Integration

## Problem Summary
The frontend was receiving a **CORS (Cross-Origin Resource Sharing)** error when trying to communicate with the backend API:

```
Access to fetch at 'http://localhost:8000/api/v1/chat/sessions' from origin
'http://localhost:3001' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### Root Cause
- **Frontend running on:** `http://localhost:3001`
- **Backend running on:** `http://localhost:8000`
- **Backend CORS configuration only allowed:** `localhost:3000`, `localhost:8080`, `localhost`
- **Missing:** `localhost:3001` was not in the CORS whitelist

## Solution Applied

### 1. ✅ Backend Configuration (backend/.env)
**Updated CORS_ORIGINS to include localhost:3001:**

```env
# Before
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080","http://localhost"]

# After
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:8080","http://localhost"]
```

### 2. ✅ Frontend API Requests (src/utils/chatApi.js)
**Added proper CORS headers to all fetch requests:**

All API endpoints now include:
```javascript
credentials: 'include'  // Send cookies with cross-origin requests
```

Updated endpoints:
- `POST /api/v1/chat/stream` - Send chat messages (streaming)
- `GET /api/v1/chat/history/{sessionId}` - Fetch conversation history
- `POST /api/v1/chat/sessions` - Create new chat session
- `GET /api/v1/health` - Health check

## How to Apply the Fix

### Step 1: Restart Backend
The backend must be restarted to load the updated `.env` configuration:

```bash
# If using Python backend:
cd backend
python main.py

# Or with uvicorn:
uvicorn main:app --reload --port 8000
```

### Step 2: Restart Frontend Dev Server
After updating the backend, restart the frontend:

```bash
# In Front-End-Book directory
npm start
# Or
yarn start
```

### Step 3: Verify the Fix
Look for these console logs to confirm successful connection:

✅ **Before the fix (errors):**
```
❌ [RootContent] ChatInterface should be hidden (isOpen=false)
❌ Failed to load resource: net::ERR_FAILED
❌ Failed to initialize chat session: Failed to create session
```

✅ **After the fix (success):**
```
✅ [RootContent] OpenAI API key injected
📊 [ChatReducer] Setting session: session_xxxxx
📨 [sendMessage] Request payload: {...}
```

## Files Modified

| File | Changes |
|------|---------|
| `backend/.env` | Added `http://localhost:3001` to CORS_ORIGINS |
| `src/utils/chatApi.js` | Added `credentials: 'include'` to all fetch calls |

## Testing the API Connection

### Option 1: Check Console Logs
Open browser DevTools (F12) and check the console for:
1. No CORS errors
2. Successful session creation message
3. Chat interface becoming available

### Option 2: Test Health Check
Run this in your browser console:
```javascript
fetch('http://localhost:8000/api/v1/health', {
  method: 'GET',
  credentials: 'include'
})
.then(r => r.json())
.then(data => console.log('✅ Backend healthy:', data))
.catch(e => console.error('❌ Backend error:', e.message))
```

### Option 3: Manual Session Creation
```javascript
fetch('http://localhost:8000/api/v1/chat/sessions', {
  method: 'POST',
  credentials: 'include'
})
.then(r => r.json())
.then(data => console.log('✅ Session created:', data))
.catch(e => console.error('❌ Session error:', e.message))
```

## Troubleshooting

### Still Getting CORS Errors?
1. **Clear browser cache:** DevTools → Network → "Disable cache" checkbox
2. **Hard refresh:** Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
3. **Restart both servers:** Backend first, then frontend

### Backend Port Already in Use
```bash
# Find and kill process on port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :8000
kill -9 <PID>
```

### Frontend Port Already in Use
```bash
# Find and kill process on port 3001
# Windows
netstat -ano | findstr :3001
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :3001
kill -9 <PID>
```

## Configuration Details

### CORS_ORIGINS Format
The CORS_ORIGINS must be a valid JSON array string:
```env
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:8080"]
```

✅ Valid formats:
- Single origin: `["http://localhost:3001"]`
- Multiple origins: `["http://localhost:3001","http://localhost:8080"]`
- Wildcards: `["http://localhost:*"]` (use cautiously)

❌ Invalid formats:
- Unquoted: `[http://localhost:3001]`
- Single quotes: `['http://localhost:3001']`
- Missing brackets: `http://localhost:3001`

### Environment Variable Loading
The backend loads CORS_ORIGINS from `.env` file. Make sure:
1. File is named exactly `.env` (not `.env.local` or `.env.development`)
2. Located in the `backend/` directory
3. Backend is restarted after changes

## Additional Improvements Made

### Fetch Request Standards
All fetch calls now follow best practices:

```javascript
// Before (minimal)
fetch(url, { method: 'POST' })

// After (proper CORS)
fetch(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',  // ← Allows authentication cookies
  body: JSON.stringify(data)
})
```

## Production Considerations

When deploying to production, update CORS_ORIGINS with actual domains:

```env
# Development
CORS_ORIGINS=["http://localhost:3001","http://localhost:8000"]

# Production
CORS_ORIGINS=["https://app.example.com","https://api.example.com"]
```

## Related Files

- Backend configuration: `/backend/.env`
- API client: `/Front-End-Book/src/utils/chatApi.js`
- Chat context: `/Front-End-Book/src/context/ChatContext.js`
- Chat interface: `/Front-End-Book/src/components/RAGChatbot/ChatInterface.jsx`

## Resources

- [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [CORS Troubleshooting Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS/Errors)
- [Fetch API Credentials](https://developer.mozilla.org/en-US/docs/Web/API/fetch#credentials)

---

**Status:** ✅ Fixed
**Date:** 2026-03-03
**Branch:** 010-content-personalization
