# Tasks: Complete Vercel Deployment (Frontend + Backend Serverless)

**Branch**: `011-vercel-deployment`
**Input**: Design documents from `/specs/011-vercel-deployment/`
**Prerequisites**: plan.md (architecture), spec.md (6 user stories P1/P2), research.md (7 decisions), data-model.md (3 entities), quickstart.md (dev setup)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. All tasks are parallelizable where marked [P].

**Tests**: NOT INCLUDED - Specification did not request test tasks. Tests can be added in a separate `/sp.tasks --tests` pass if needed.

---

## Format: `- [ ] [TaskID] [P] [Story] Description with file path`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5, US6)
- **File paths**: Absolute paths for clarity

---

## Phase 1: Setup (Project Initialization & Infrastructure)

**Purpose**: Create basic Vercel monorepo structure and dependencies

### Setup Tasks

- [x] T001 Create /api directory structure with subdirectories: api/auth/, api/contracts/
- [x] T002 [P] Create api/requirements.txt with pinned dependency versions: FastAPI, neondb, passlib[bcrypt], PyJWT, openai, python-multipart
- [x] T003 [P] Create vercel.json in repository root with build configuration (Docusaurus static + Python serverless routes)
- [x] T004 [P] Create .env.production file in Front-End-Book/ with REACT_APP_API_URL=/api
- [x] T005 [P] Create .gitignore entries for: .env, .env.*.local, api/__pycache__, api/.pytest_cache, Front-End-Book/build/

**Checkpoint**: Project structure initialized - dependencies listed - deployment config ready

---

## Phase 2: Foundational Infrastructure (CRITICAL - Blocks All User Stories)

**Purpose**: Shared utilities that all serverless functions depend on

### Foundational Tasks

- [x] T006 Create api/_middleware.py with:
  - Database connection helper using Neon serverless driver (asyncpg + pgBouncer)
  - JWT token generation function (HS256, 7-day expiration, 30-day remember_me)
  - JWT token verification function
  - CORS headers function (Access-Control-Allow-Origin, Credentials, Methods)
  - Password hashing utility using passlib + bcrypt
  - Error response formatter (consistent error JSON)
  - Request body parser helper

- [x] T007 [P] Create api/auth/ directory with init files (created signup.py and signin.py)

- [x] T008 [P] Create database schema initialization script:
  - Created api/init_db.py with idempotent CREATE TABLE statements
  - users table (id, email UNIQUE, password_hash, full_name, is_active, created_at, updated_at)
  - user_backgrounds table (id, user_id FK, software_background, hardware_background, ros_experience, python_level, learning_goal, available_hardware, timestamps)
  - conversation_histories table (id, user_id FK, conversation_id, role, message, tokens_used, created_at)
  - All indexes and constraints as defined in data-model.md

- [x] T009 Create front-end API client configuration:
  - Updated Front-End-Book/src/context/AuthContext.tsx to use REACT_APP_API_URL environment variable
  - All auth endpoints now call ${API_BASE_URL}/api/auth/* dynamically (signin, signup, signout, profile, update)
  - chatApi.js already had environment variable configuration (no changes needed)
  - All API URLs now respect REACT_APP_API_URL from environment or default to localhost:8000

**Checkpoint**: Foundation complete - all shared utilities ready - database schema deployed - frontend API client pointing to /api routes

---

## Phase 3: User Story 1 - Deploy Frontend to Production (Priority: P1) 🎯 MVP

**Goal**: Get Docusaurus static site live on Vercel CDN with fast load times and automatic redeploy on GitHub push

**Independent Test**: Visit production URL, homepage loads in < 3 seconds, all navigation works, theme toggle switches light/dark mode, page persists across refreshes

### Implementation for User Story 1

- [ ] T010 [US1] Build Docusaurus production bundle:
  - cd Front-End-Book && npm run build
  - Verify build/ folder created with index.html, assets/
  - Check for build errors or warnings
  - Verify bundle size is reasonable

- [ ] T011 [US1] Configure Docusaurus build in vercel.json:
  - Set build source: "Front-End-Book/package.json"
  - Set build output directory: "Front-End-Book/build"
  - Set install command: "cd Front-End-Book && npm install"
  - Set build command: "cd Front-End-Book && npm run build"

- [ ] T012 [US1] Create Vercel project and GitHub integration:
  - Go to vercel.com
  - Create new project
  - Import GitHub repository (Hackathon-1)
  - Authorize Vercel to GitHub
  - Select branch: main
  - Vercel auto-detects Docusaurus and configures build

- [ ] T013 [US1] Verify Vercel deployment settings:
  - Framework Preset: Docusaurus (or auto-detected)
  - Build Command: cd Front-End-Book && npm run build
  - Output Directory: Front-End-Book/build
  - Install Command: cd Front-End-Book && npm install
  - Environment: (empty for now, add in Phase 4)
  - Click Deploy to trigger first build

- [ ] T014 [US1] Monitor first deployment:
  - Watch Vercel build logs in dashboard
  - Check for errors (missing dependencies, broken imports)
  - Verify build completes successfully
  - Check deployment URL is live (will be something like https://hackathon-1-vercel.app)

- [ ] T015 [US1] Test frontend deployment:
  - Visit production URL in browser
  - Verify homepage loads (< 3 seconds)
  - Check all navigation links work (HOME, MODULE 1-4)
  - Test theme toggle (light/dark mode)
  - Verify theme preference persists on reload
  - Test responsive design (resize browser to mobile width)

**Checkpoint**: Frontend is live on Vercel, loads fast, all navigation works, theme toggle functional

---

## Phase 4: User Story 2 - Deploy Backend Serverless Functions (Priority: P1)

**Goal**: Convert FastAPI endpoints to Vercel Serverless Functions, deploy to /api routes, enable CORS for frontend

**Independent Test**: Call curl http://localhost:3000/api/auth/signup → 201 response with access_token; Call curl http://localhost:3000/api/me with Bearer token → 200 response with user data; CORS headers present in response

### Implementation for User Story 2

- [ ] T016 [US2] Create api/auth/signup.py serverless function:
  - Import BaseHTTPRequestHandler, json, os, passlib, neondb
  - Create handler class with do_POST method
  - Parse JSON request body (email, password, full_name, optional background fields)
  - Validate email format (must contain @ and .)
  - Validate password (min 6 chars, contains letter + number) - use regex from schema validation
  - Check for duplicate email in database
  - Hash password using bcrypt (cost factor 12)
  - Insert new user into users table
  - Insert user_background if provided
  - Generate JWT token with user email
  - Set CORS headers via _middleware.add_cors_headers()
  - Return JSON response: {access_token, token_type: "bearer", expires_in: 604800}
  - Error handling: return 400 (validation), 409 (duplicate email), 500 (database error)

- [ ] T017 [US2] Create api/auth/signin.py serverless function:
  - Import BaseHTTPRequestHandler, json, os
  - Create handler class with do_POST method
  - Parse JSON request body (email, password, remember_me?)
  - Query database for user by email
  - Verify password using passlib.verify
  - Generate JWT token (7-day or 30-day based on remember_me)
  - Set CORS headers
  - Return JSON response: {access_token, token_type, expires_in}
  - Error handling: return 401 (invalid credentials), 500 (database error)

- [ ] T018 [US2] Create api/translate.py serverless function:
  - Require JWT authentication (check Authorization header)
  - Import OpenAI SDK
  - Parse JSON request body (text, target_language)
  - Call OpenAI API for Urdu translation: "Translate to Urdu: {text}"
  - Return JSON response: {translated_text}
  - Error handling: return 401 (invalid token), 400 (missing fields), 500 (API error)
  - Set CORS headers

- [ ] T019 [US2] Create api/personalize.py serverless function:
  - Require JWT authentication
  - Parse JSON request body (quiz_answers)
  - Call OpenAI API to generate personalized content recommendations
  - Return JSON response: {personalization_data}
  - Error handling: return 401, 400, 500
  - Set CORS headers

- [ ] T020 [US2] Create api/chat.py serverless function (RAG chatbot):
  - Require JWT authentication
  - Parse JSON request body (message, conversation_id?)
  - Generate conversation_id if not provided (uuid4)
  - Store user message in conversation_histories table
  - Call OpenAI API with RAG context from Qdrant/Vector DB
  - Store assistant response in conversation_histories table
  - Return JSON response: {response, conversation_id}
  - Error handling: return 401, 400, 500
  - Set CORS headers

- [ ] T021 [US2] Update api/requirements.txt with all dependencies:
  - FastAPI==0.104.1 (for type hints and error handling used in converted code)
  - neon-api-python==0.4.0 (Neon serverless driver)
  - psycopg2-binary==2.9.9 (PostgreSQL adapter)
  - PyJWT==2.8.1 (JWT token generation and verification)
  - passlib[bcrypt]==1.7.4 (Password hashing)
  - openai==1.3.9 (OpenAI API client)
  - python-multipart==0.0.6 (Form parsing)

- [ ] T022 [US2] Update vercel.json for Python serverless routes:
  - Add builds section: "src": "api/**/*.py", "use": "@vercel/python"
  - Add routes section: {"src": "/api/(.*)", "dest": "/api/$1"}
  - Verify existing Docusaurus build config is preserved

- [ ] T023 [US2] Test locally with vercel dev:
  - Run: vercel dev
  - Test signup endpoint: curl -X POST http://localhost:3000/api/auth/signup -d '{"email":"test@example.com","password":"Test123","full_name":"Test"}'
  - Verify 201 response with access_token
  - Test signin endpoint: curl -X POST http://localhost:3000/api/auth/signin -d '{"email":"test@example.com","password":"Test123"}'
  - Verify 200 response with valid JWT
  - Test CORS headers: curl -i http://localhost:3000/api/auth/signup
  - Verify Access-Control-Allow-Origin, Credentials, Methods headers present
  - Check database: user inserted in Neon

**Checkpoint**: All 5 serverless functions created, tested locally, ready for Vercel deployment

---

## Phase 5: User Story 3 - Public User Registration Works End-to-End (Priority: P1)

**Goal**: Users can sign up with any email (Gmail, Yahoo, etc.), login, and access protected features

**Independent Test**: Sign up with newuser@gmail.com, password Test123, get JWT token, use token to access profile endpoint, verify user data returned

### Implementation for User Story 3

- [ ] T024 [US3] Ensure signup endpoint ACCEPTS ANY EMAIL:
  - Remove any domain restrictions from api/auth/signup.py
  - Validate only: email contains @, email contains ., email is unique in database
  - Test: curl signup with random@gmail.com, random@yahoo.com, name@company.co.uk
  - Verify all succeed with 201 response

- [ ] T025 [US3] Create api/me endpoint for getting current user profile:
  - Require JWT authentication
  - Extract email from JWT token payload
  - Query users table by email
  - Return JSON response: {id, email, full_name, is_active, created_at, background}
  - Error handling: 401 (invalid token), 500 (user not found)
  - Set CORS headers

- [ ] T026 [US3] Create api/signout endpoint:
  - Accept POST request with Authorization header
  - Verify JWT is valid (no database operation needed, tokens are stateless)
  - Return JSON response: {message: "Successfully signed out"}
  - Set CORS headers

- [ ] T027 [US3] Test full signup→signin→profile flow:
  - Step 1: Sign up with newemail@example.com, password NewPass123
  - Receive access_token
  - Step 2: Store token in local variable: TOKEN="..."
  - Step 3: Sign in with same credentials
  - Receive new token
  - Step 4: Call /api/me with Authorization: Bearer $TOKEN
  - Verify response includes user data
  - Step 5: Verify user_background data saved correctly

- [ ] T028 [US3] Test password validation and duplicate prevention:
  - Test weak password (5 chars): Should return 400
  - Test no number: Should return 400
  - Test no letter: Should return 400
  - Test duplicate email: Should return 409
  - Test valid password (6+ chars, letter + number): Should return 201

- [ ] T029 [US3] Test on production Vercel:
  - Wait for frontend → signup form appears
  - Sign up with judge@hackathon.com, password Judge123
  - Get redirected to profile/dashboard (verify frontend integration)
  - Verify user appears in Neon database
  - Sign out and back in with same credentials

**Checkpoint**: Public signup fully functional, any email accepted, full auth flow works (signup → signin → profile → signout)

---

## Phase 6: User Story 4 - Database Connection to Neon Postgres Works (Priority: P1)

**Goal**: All serverless functions write/read data to Neon persistently, handle connection pooling, no timeouts

**Independent Test**: Sign up → data appears in Neon; Query returns correct user record; Concurrent requests don't timeout; Function restart reconnects automatically

### Implementation for User Story 4

- [ ] T030 [US4] Verify Neon database connection in api/_middleware.py:
  - Test connection string from DATABASE_URL env var
  - Create get_db_connection() function using Neon serverless driver
  - Set connection timeout: 10 seconds
  - Set statement timeout: 30 seconds
  - Verify pgBouncer connection pooling enabled

- [ ] T031 [US4] Add retry logic for database connections in api/_middleware.py:
  - Implement exponential backoff (100ms, 200ms, 400ms)
  - Max 3 retries on connection timeout
  - Return 503 if all retries fail

- [ ] T032 [US4] Test data persistence:
  - Sign up user: curl signup → user1@test.com
  - Query Neon directly: psql $DATABASE_URL
  - SELECT * FROM users WHERE email='user1@test.com'
  - Verify user row exists with correct password hash and created_at
  - Test user_backgrounds insertion: Sign up with background data
  - SELECT * FROM user_backgrounds WHERE user_id=[id]
  - Verify all fields saved correctly

- [ ] T033 [US4] Test concurrent requests don't exhaust connections:
  - Start 5 parallel signup requests: for i in {1..5}; do curl signup ... & done
  - All should succeed with 201 response
  - Check Neon connection count in dashboard
  - Verify connection pool reused, not creating 5 new connections

- [ ] T034 [US4] Test connection pool survives cold-starts:
  - Deploy to Vercel (Phase 5)
  - Wait 30 minutes for function to go cold
  - Call /api/auth/signin
  - Verify response time < 5 seconds (includes cold-start)
  - Verify correct user data returned
  - Call /api/auth/signin again within 1 minute
  - Verify response time < 2 seconds (warm start)

- [ ] T035 [US4] Add logging for database operations:
  - Log connection: "Connected to Neon: [timestamp]"
  - Log queries: "Query: [query] - [duration]ms"
  - Log errors: "DB Error: [error] - Retrying..."
  - Verify logs appear in Vercel Function logs dashboard

**Checkpoint**: Database connection tested, concurrent access safe, cold-start handling verified, persistent storage confirmed

---

## Phase 7: User Story 5 - All Features Work in Production (Priority: P2)

**Goal**: Translation, personalization, and RAG chatbot features operational with serverless backend and Neon database

**Independent Test**: Translate text to Urdu via API, get personalization recommendations, ask chatbot question and get RAG response

### Implementation for User Story 5

- [ ] T036 [US5] Test translation feature end-to-end:
  - Sign up user, get JWT token
  - Call /api/translate with JWT: curl -H "Authorization: Bearer $TOKEN" -d '{"text":"Hello world","target_language":"ur"}'
  - Verify 200 response with Urdu translation
  - Test invalid token: should return 401
  - Test missing text: should return 400

- [ ] T037 [US5] Test personalization feature end-to-end:
  - Sign up user with background questionnaire data
  - Call /api/personalize with JWT and quiz answers
  - Verify 200 response with personalization recommendations
  - Test 3 levels: beginner, intermediate, advanced
  - Verify different recommendations returned for each level

- [ ] T038 [US5] Test RAG chatbot feature end-to-end:
  - Sign up user, get JWT token
  - Call /api/chat with JWT: curl -H "Authorization: Bearer $TOKEN" -d '{"message":"What is ROS 2?"}'
  - Verify 200 response with AI response (should be grounded in course content)
  - Test conversation_id: Store returned conversation_id
  - Call /api/chat again with same conversation_id and new message
  - Verify conversation history preserved
  - Verify response time < 5 seconds

- [ ] T039 [US5] Test all 4 bonus features on live Vercel deployment:
  - Frontend: Navigate to each module
  - Test Urdu translation: Select text → Translate → Verify Urdu
  - Test Personalization: Open personalization settings → Change level → Content updates
  - Test RAG Chatbot: Open chatbot → Ask course question → Get answer
  - Test Better-auth integration: User profile page shows correct data

- [ ] T040 [US5] Verify feature response times meet SLA:
  - Translation: < 5 seconds (OpenAI API call + overhead)
  - Personalization: < 5 seconds (OpenAI API call + overhead)
  - RAG Chat: < 5 seconds (Vector DB + OpenAI API call)
  - Monitor in Vercel dashboard → Functions → Execution logs

**Checkpoint**: All 4 bonus features fully functional in production, SLAs met, user experience smooth

---

## Phase 8: User Story 6 - Zero-Downtime Deployment (Priority: P2)

**Goal**: Deploy updates without downtime, use Vercel's blue-green deployment automatically

**Independent Test**: Deploy new version → old version still live during build → switch to new version when ready → rollback if needed

### Implementation for User Story 6

- [ ] T041 [US6] Enable automatic Vercel deployments on GitHub push:
  - Verify GitHub app connected to Vercel project
  - Verify branch protection rule: require PR review (optional but recommended)
  - Each push to main branch triggers Vercel build
  - Check Vercel dashboard: Deployments tab shows all builds

- [ ] T042 [US6] Test zero-downtime deployment process:
  - Make code change (e.g., update vercel.json comment)
  - Push to main branch
  - Vercel starts build (shown as "In Progress" in dashboard)
  - While building, call /api/auth/signin (old deployment still live)
  - Verify request succeeds from old version
  - Build completes
  - Vercel automatically promotes new build to Production
  - Verify /api/auth/signin still works (now from new version)
  - Check Deployment URL to confirm it's new build

- [ ] T043 [US6] Test rollback capability:
  - If new deployment has errors, use Vercel dashboard
  - Go to Deployments → Find previous known-good deployment
  - Click three dots → "Promote to Production"
  - Verify Promoted deployment is now active
  - Check that features work with old version

**Checkpoint**: Automatic deployments working, blue-green switching transparent, rollback verified

---

## Phase 9: Integration Testing (Production Verification)

**Purpose**: Verify all user stories work together in production environment

### Integration Tests

- [ ] T044 Full user journey test:
  - Step 1: Visit https://your-project.vercel.app (frontend loads < 3s)
  - Step 2: Click Sign Up
  - Step 3: Sign up with newemail@test.com, password NewPass123
  - Step 4: Complete background questionnaire
  - Step 5: Get redirected to dashboard
  - Step 6: Verify profile shows correct user data
  - Step 7: Test translate feature (select text → translate)
  - Step 8: Test personalization (change learning level)
  - Step 9: Test RAG chatbot (ask question)
  - Step 10: Sign out (click logout)
  - Step 11: Verify redirected to homepage
  - Step 12: Sign in with same credentials
  - Verify all steps complete without errors

- [ ] T045 Mobile responsive test:
  - Open https://your-project.vercel.app on mobile or mobile DevTools
  - Verify layout adapts to mobile width
  - Test signup form on mobile
  - Test navigation on mobile
  - Test chatbot on mobile
  - Verify buttons are touch-friendly (minimum 44x44px)

- [ ] T046 CORS security test:
  - Open browser Developer Tools → Network tab
  - Make API call from frontend
  - Verify CORS headers present:
    - Access-Control-Allow-Origin: https://your-project.vercel.app
    - Access-Control-Allow-Credentials: true
  - Test OPTIONS preflight request for POST endpoints
  - Verify no 403 errors in console

- [ ] T047 JWT token security test:
  - Sign in, get token
  - Modify token: echo $TOKEN | sed 's/.$/X/' > token_modified.txt
  - Call /api/me with modified token
  - Verify 401 response (invalid signature)
  - Wait 7 days (or modify token to have past exp time)
  - Verify 401 response (token expired)

- [ ] T048 Performance baseline check:
  - Frontend: Load https://your-project.vercel.app
  - Check Lighthouse score (should be 80+)
  - Check First Contentful Paint < 3 seconds
  - API: Call endpoints, check response time < 2 seconds
  - Database: Verify queries respond < 1 second
  - Document baseline metrics for comparison

**Checkpoint**: All user journeys work end-to-end, security verified, performance acceptable

---

## Phase 10: Final Verification & Documentation

**Purpose**: Confirm all 300 points functionality, document production URLs, prepare for demo

### Final Tasks

- [ ] T049 Verify all 5 base features + 4 bonus features operational:
  - Base 1: Docusaurus documentation ✅
  - Base 2: RAG chatbot ✅
  - Base 3: User authentication ✅
  - Base 4: Module navigation ✅
  - Base 5: Theme toggle (light/dark) ✅
  - Bonus 1: Urdu translation ✅
  - Bonus 2: Content personalization ✅
  - Bonus 3: Better-auth user profiles ✅
  - Bonus 4: Responsive UI/UX ✅

- [ ] T050 Document production URLs:
  - Frontend: https://your-project.vercel.app
  - API Base: https://your-project.vercel.app/api
  - Auth Endpoints: /api/auth/signup, /api/auth/signin
  - Feature Endpoints: /api/translate, /api/personalize, /api/chat
  - Save to README.md or DEPLOYMENT_URLS.txt

- [ ] T051 Create Deployment Verification Checklist (for demo):
  - ✅ Frontend loads in < 3 seconds
  - ✅ Theme toggle works (light/dark)
  - ✅ Navigation to all modules works
  - ✅ Signup with any email works
  - ✅ JWT authentication working
  - ✅ Translation feature works (select text → translate)
  - ✅ Personalization feature works (3 levels)
  - ✅ RAG chatbot responds to questions
  - ✅ User profile shows correct data
  - ✅ Responsive on mobile
  - ✅ API endpoints respond < 2 seconds
  - ✅ Database queries persistent

- [ ] T052 Prepare demo video content:
  - Record: Homepage load
  - Record: User signup flow
  - Record: Signing in and accessing profile
  - Record: Using translation feature
  - Record: Using personalization feature
  - Record: Using RAG chatbot
  - Record: Mobile responsive view
  - Verify video shows all 5 + 4 features clearly
  - Upload to GitHub or submission platform

- [ ] T053 Run through quickstart.md validation:
  - Follow all local development steps (from specs/011-vercel-deployment/quickstart.md)
  - Verify vercel dev works locally
  - Verify curl commands succeed
  - Verify CORS headers correct
  - Document any issues found

**Checkpoint**: All functionality verified, production ready, demo prepared

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends On | Purpose | Blocking |
|-------|-----------|---------|----------|
| Phase 1 (Setup) | Nothing | Project structure, config | No - can start immediately |
| Phase 2 (Foundational) | Phase 1 ✅ | Shared utilities, database | **YES - blocks all stories** |
| Phase 3 (US1) | Phase 2 ✅ | Frontend deployment | No - can run parallel with US2+ |
| Phase 4 (US2) | Phase 2 ✅ | Backend functions | No - can run parallel with US1, US3+ |
| Phase 5 (US3) | Phase 4 ✅ | Auth integration | Depends on Phase 4 complete |
| Phase 6 (US4) | Phase 4 ✅ | Database persistence | Runs alongside Phase 4-5 |
| Phase 7 (US5) | Phase 4 ✅ | Feature endpoints | Depends on Phase 4 complete |
| Phase 8 (US6) | Phase 3 ✅ | Deployment automation | Runs after Phase 3 |
| Phase 9 (Integration) | Phases 3-8 | Full journey test | Verifies all phases complete |
| Phase 10 (Final) | Phases 3-9 | Documentation & demo | Last phase before submission |

### Critical Path (Longest Sequence)

```
Phase 1 (Setup)
  → Phase 2 (Foundational)
    → Phase 3 (Frontend) + Phase 4 (Backend) in parallel
      → Phase 5 (Auth) + Phase 6 (Database) + Phase 7 (Features)
        → Phase 8 (Deployments)
          → Phase 9 (Integration)
            → Phase 10 (Demo)
```

### Parallel Opportunities

**After Phase 1 completes**:
- All Phase 2 tasks marked [P] run in parallel

**After Phase 2 completes**:
- Phase 3 (Frontend) and Phase 4 (Backend) can run in PARALLEL
- If 2 developers: Dev A → Frontend, Dev B → Backend
- If 1 developer: Frontend first (faster), then Backend

**After Phase 4 completes**:
- Phase 5 (Auth), Phase 6 (Database), Phase 7 (Features) can run IN PARALLEL
- Phase 8 (Deployments) runs after Phase 3
- Phase 9 (Integration) must wait for all to complete

---

## Implementation Strategy

### MVP First (Fast Demo) - 70 minutes

1. **Phase 1 + 2**: Setup + Foundational (20 min)
   - Create folder structure, _middleware.py, vercel.json
   - Create database schema in Neon
   - Update frontend API endpoints

2. **Phase 3**: Frontend (10 min)
   - npm run build
   - Deploy to Vercel
   - Test homepage loads

3. **Phase 4 + 5**: Backend + Auth (20 min)
   - Create signup.py, signin.py
   - Create /api/me endpoint
   - Test signup/signin locally with vercel dev

4. **Phase 9 + 10**: Integration + Demo (20 min)
   - Test full user journey: signup → signin → profile
   - Record demo video
   - Document production URLs

**At this point**: 5 base features complete, 2 bonus features (auth + personalization from background), SUBMITTABLE

### Full Feature Set - Additional 20 minutes

5. **Phase 7**: Features (10 min)
   - Create translate.py, personalize.py, chat.py

6. **Phase 8 + 9**: Deployments + Full Integration (10 min)
   - Test all features end-to-end
   - Verify CORS, JWT, database persistence
   - Mobile responsive test

---

## Task Execution Checklist

### Before Starting Any Task
- [ ] Read the task description completely
- [ ] Understand the file path and dependencies
- [ ] Check if task is [P] (can run in parallel)
- [ ] Verify all blocking tasks are complete

### While Executing a Task
- [ ] Create file/function per specification
- [ ] Test locally (vercel dev or direct execution)
- [ ] Verify success criteria met
- [ ] Check for errors in Vercel logs (if deployed)

### After Completing a Task
- [ ] Mark checkbox: `- [x]`
- [ ] Run git add, git commit
- [ ] Move to next task OR wait for blocking tasks
- [ ] At checkpoints: test current milestone independently

---

## Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Neon connection timeout | MEDIUM | Use async driver, retry logic, connection pooling |
| 50MB function size limit | LOW | Monitor dependencies, exclude test files |
| CORS 403 errors | MEDIUM | Test with curl -i before production, verify headers |
| Cold-start slowness | MEDIUM | Expected 1-2s, use connection pooling for faster reconnect |
| JWT token validation fails | LOW | Test locally with vercel dev first, verify secret matches |
| GitHub webhook delays | LOW | Vercel queues builds, usually < 2 minutes |
| Database schema mismatch | LOW | Apply schema once, verify in Neon dashboard |

---

## Success Criteria (All Must Be ✅)

- [ ] Frontend deployed and live at production URL
- [ ] All 5 serverless functions created and tested
- [ ] Public signup works with any email
- [ ] JWT authentication verified
- [ ] Database persistence tested
- [ ] All 4 bonus features operational
- [ ] CORS headers correctly configured
- [ ] Performance: Frontend < 3s, API < 2s, Signup < 5s
- [ ] Mobile responsive design verified
- [ ] Full user journey tested end-to-end
- [ ] Production URLs documented
- [ ] Demo video recorded

---

## Estimated Timeline

| Phase | Duration | Notes |
|-------|----------|-------|
| Phase 1: Setup | 5 min | Folder creation, config files |
| Phase 2: Foundational | 15 min | _middleware.py, database schema, API client updates |
| Phase 3: Frontend | 10 min | npm build, Vercel deployment |
| Phase 4: Backend (5 functions) | 20 min | Convert endpoints, test locally |
| Phase 5: Auth Integration | 5 min | Profile endpoint, flow testing |
| Phase 6: Database Verification | 10 min | Persistence, concurrency, cold-start |
| Phase 7: Bonus Features | 10 min | Translate, personalize, chat |
| Phase 8: Deployments | 5 min | Automation, rollback verification |
| Phase 9: Integration Testing | 10 min | Full journey, mobile, CORS |
| Phase 10: Final Verification | 10 min | Documentation, demo prep |
| **Buffer** | **10 min** | Contingency for issues |
| **TOTAL** | **~100 minutes** | Aggressive but achievable |

---

## Notes

- Each task should take the time estimate. If taking longer, check for blockers.
- Mark each task complete (`- [x]`) before moving on
- At checkpoints, stop and verify that story works independently
- Commit changes frequently (after each task or logical group)
- Use Vercel logs and local vercel dev for debugging
- All file paths are absolute from repository root
- Tests are NOT included in this task list (specification didn't request them)

**Ready to execute!** Start with Phase 1: Setup.
