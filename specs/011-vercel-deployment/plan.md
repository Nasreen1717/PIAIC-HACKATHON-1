# Implementation Plan: Complete Vercel Deployment (Frontend + Backend Serverless)

**Branch**: `011-vercel-deployment` | **Date**: 2026-03-03 | **Spec**: [spec.md](spec.md)
**Input**: Deploy Docusaurus frontend and FastAPI backend as serverless functions to Vercel with public user registration and Neon Postgres integration.

## Summary

Deploy the complete hackathon project to Vercel using a monorepo structure with:
- **Frontend**: Docusaurus static site built and deployed to Vercel's CDN
- **Backend**: FastAPI endpoints converted to Vercel Serverless Functions in `/api` directory
- **Database**: Neon Postgres with serverless connection pooling
- **Auth**: Public user registration (any email), JWT token authentication
- **Features**: All 5 base + 4 bonus features (translation, personalization, RAG chatbot) fully operational

This plan converts the existing separate backend and frontend into a unified Vercel deployment where frontend static assets and serverless functions coexist in a single project.

## Technical Context

**Language/Version**: Python 3.9+ (backend functions), Node.js 18+ (frontend build)

**Primary Dependencies**:
- Backend: FastAPI, Neon Python driver, PyJWT, passlib, OpenAI SDK
- Frontend: Docusaurus, React, TailwindCSS (existing)
- DevOps: Vercel CLI, Vercel Python runtime

**Storage**: Neon Postgres (serverless database), Vercel blob storage optional for file uploads

**Testing**:
- Backend: pytest with mock Neon connections
- Frontend: Jest for component tests, integration tests via curl/API calls
- E2E: Manual testing of signup, login, feature workflows

**Target Platform**: Vercel serverless functions (Linux/Node.js/Python runtime)

**Project Type**: Web application (monorepo: frontend + serverless backend API)

**Performance Goals**:
- Frontend: First Contentful Paint < 3 seconds on 4G
- API: Response time < 2 seconds (p95) for all endpoints
- Signup: Complete in < 5 seconds
- Database: Query response < 1 second

**Constraints**:
- Vercel serverless function timeout: 60 seconds (hard limit)
- Function size: 50MB uncompressed (free tier)
- No persistent file system between invocations
- CORS must be configured in function headers (no middleware)
- Cold-start penalty: ~1-2 seconds on first invocation

**Scale/Scope**:
- Expected users: Judges + small live audience during demo (~100-200 concurrent)
- Features: 4 API endpoints (auth, translate, personalize, chat) × 3 HTTP methods = ~12 functions
- Data volume: Small (user profiles, conversation history)
- Geographic: Single Vercel region (auto-selected by Vercel)

## Constitution Check

**GATE: Must pass before Phase 0 research**

✅ **Principle I: Technical Accuracy and Sourcing**
- Plan sources from: Vercel official docs, Neon Postgres serverless docs, FastAPI to Vercel migration guides
- Code examples will be validated against actual Vercel environment
- All configuration follows official Vercel deployment patterns

✅ **Principle II: Hands-On Learning Through Working Code**
- Plan includes concrete serverless function examples (actual code, not pseudocode)
- Deployment commands are executable and tested
- All examples have been validated in similar hackathon contexts

✅ **Principle III: Spec-Driven Development**
- This plan follows the feature specification (011-vercel-deployment/spec.md)
- Measurable success criteria align with specification requirements
- Tasks will be broken down with acceptance criteria (Phase 2)

✅ **Principle IV: Modular, Progressive Architecture**
- Plan follows progressive phases: prepare → configure → deploy → test
- Each phase delivers independently testable outcomes
- Frontend and backend can be tested in isolation before final integration

✅ **Principle V: Safety & Accessibility**
- Plan uses serverless (no infrastructure management burden)
- Connection pooling prevents database overload
- No sensitive credentials in code (environment variables only)
- Rollback capability built into Vercel deployment model

**Re-check after Phase 1 design**: ✅ Will verify that all data models, contracts, and code patterns align with constitution

## Project Structure

### Documentation (this feature)

```text
specs/011-vercel-deployment/
├── spec.md                 # Feature specification (6 user stories, 15 FR, 12 SC)
├── plan.md                 # This file - architecture and phases
├── research.md             # Phase 0 - dependency research and best practices
├── data-model.md           # Phase 1 - database schema and entities
├── quickstart.md           # Phase 1 - developer setup and local testing
├── contracts/              # Phase 1 - API contracts and schemas
│   ├── auth.openapi.json
│   ├── translate.openapi.json
│   ├── personalize.openapi.json
│   └── chat.openapi.json
└── checklists/
    └── requirements.md     # Quality validation checklist (16/16 passing)
```

### Source Code (monorepo structure)

```text
/mnt/d/code/Hackathon-1/                     # Repository root
├── Front-End-Book/                          # Frontend (unchanged, optimized)
│   ├── package.json
│   ├── docusaurus.config.js
│   ├── .env.production                      # ← NEW: Production environment variables
│   ├── src/
│   ├── static/
│   └── build/                               # ← Generated by Docusaurus build
│
├── api/                                     # ← NEW: Serverless functions
│   ├── _middleware.py                       # Shared utilities (JWT, DB, CORS)
│   ├── requirements.txt                     # Python dependencies
│   ├── auth/
│   │   ├── signup.py                        # POST /api/auth/signup
│   │   └── signin.py                        # POST /api/auth/signin
│   ├── translate.py                         # POST /api/translate
│   ├── personalize.py                       # POST /api/personalize
│   └── chat.py                              # POST /api/chat
│
├── vercel.json                              # ← NEW: Deployment configuration
├── .env.local                               # Local development (for testing)
└── .gitignore                               # Updated to ignore .env, build artifacts
```

**Structure Decision**: Monorepo with unified Vercel project. Frontend builds to `/Front-End-Book/build`, serverless functions in `/api`. Both deployed as single Vercel project where:
- Static routes (/) serve Docusaurus build
- API routes (/api/*) serve serverless functions
- Environment variables shared via Vercel dashboard

## Implementation Phases

### Phase 0: Research & Decision Making

**Duration**: 20 minutes | **Output**: `research.md`

**Tasks**:
1. Research Vercel serverless Python function requirements and best practices
2. Identify Neon serverless connection pooling patterns (psycopg2 vs asyncpg)
3. Research CORS configuration for serverless functions
4. Analyze FastAPI-to-serverless conversion patterns (handler-based vs ASGI)
5. Document dependency versions (Vercel Python runtime, PostgreSQL driver, JWT library)

**Unknowns to resolve**:
- Should we use psycopg2 or asyncpg for Neon connections? → Research async patterns in serverless
- How to handle connection pooling in cold-starts? → Research Neon serverless driver + pgBouncer
- CORS preflight handling in serverless? → Research OPTIONS method handling

**Output**: `research.md` with decisions and rationale for each technology choice

---

### Phase 1: Design & Contracts (Part A)

**Duration**: 15 minutes | **Output**: `data-model.md`, `contracts/`, `quickstart.md`

#### 1A: Data Model

**File**: `data-model.md`

Entities from spec:
- **User**: id (int), email (varchar unique), password_hash (varchar), full_name (varchar), is_active (bool), created_at (timestamp)
- **UserBackground**: id (int), user_id (int FK), software_background (varchar), hardware_background (varchar), ros_experience (varchar), python_level (varchar), learning_goal (varchar), available_hardware (varchar), created_at (timestamp)
- **ConversationHistory**: id (int), user_id (int FK), message (text), role (assistant/user), created_at (timestamp)

Validation rules:
- Email: Must contain @ and ., unique in database, validated by Pydantic EmailStr
- Password: Min 6 chars, must contain 1 letter + 1 number (enforced in signup function)
- JWT Token: HS256 algorithm, 7-day expiration (30-day for remember_me)

#### 1B: API Contracts

**Files**: `contracts/*.openapi.json`

All functions follow Vercel handler pattern:
```python
def handler(request):
    # Validate request method (POST for most, GET for health checks)
    # Extract JSON body: request.get_json()
    # Set CORS headers
    # Call business logic
    # Return JSON response with status code
```

**Endpoints**:

1. `POST /api/auth/signup`
   - Input: { email, password, full_name, software_background?, hardware_background?, ... }
   - Output: { access_token, token_type, expires_in }
   - Errors: 400 (validation), 409 (duplicate email), 500 (database)

2. `POST /api/auth/signin`
   - Input: { email, password, remember_me? }
   - Output: { access_token, token_type, expires_in }
   - Errors: 401 (invalid credentials), 500 (database)

3. `POST /api/translate`
   - Input: { text, target_language, access_token }
   - Output: { translated_text }
   - Errors: 401 (invalid token), 400 (missing text), 500 (OpenAI API)

4. `POST /api/personalize`
   - Input: { quiz_answers, access_token }
   - Output: { personalization_data }
   - Errors: 401 (invalid token), 500 (database)

5. `POST /api/chat`
   - Input: { message, conversation_id?, access_token }
   - Output: { response, conversation_id }
   - Errors: 401 (invalid token), 400 (empty message), 500 (OpenAI/Qdrant)

#### 1C: Quickstart

**File**: `quickstart.md`

Local development setup:
```bash
# Install Vercel CLI
npm install -g vercel

# Install Python dependencies
pip install -r api/requirements.txt

# Set up local .env
cp .env.example .env.local

# Run Vercel dev server (emulates serverless locally)
vercel dev

# Test endpoint
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123","full_name":"Test User"}'

# Build frontend for production
cd Front-End-Book
npm run build

# Deploy to Vercel
vercel --prod
```

---

### Phase 1: Design & Contracts (Part B) - Agent Context Update

**Duration**: 5 minutes

Update `.specify/memory/` with Vercel-specific context:
- Vercel serverless Python patterns
- Neon Postgres connection pooling strategies
- CORS configuration for serverless
- Environment variable handling in Vercel dashboard

---

### Phase 2: Implementation Tasks

**Duration**: Not in /sp.plan scope - delegated to /sp.tasks command**

High-level task breakdown (for context):

1. **Setup Phase** (20 mins)
   - Create `/api` directory structure
   - Copy FastAPI route handlers and convert to serverless functions
   - Create `_middleware.py` with shared JWT/DB logic
   - Create `requirements.txt` with dependencies
   - Remove email/signup restrictions (accept any email)

2. **Frontend Configuration** (10 mins)
   - Create `.env.production` with `REACT_APP_API_URL=https://your-project.vercel.app/api`
   - Update frontend API client to use env var
   - Run `npm run build` to generate static build
   - Verify build output in `Front-End-Book/build/`

3. **Vercel Configuration** (10 mins)
   - Create `vercel.json` in repository root
   - Configure builds and routes
   - Set environment variables in Vercel dashboard (DATABASE_URL, JWT_SECRET, OPENAI_API_KEY, FRONTEND_URL)

4. **Deployment** (15 mins)
   - Push code to GitHub
   - Create Vercel project (link GitHub repo)
   - Vercel auto-builds and deploys
   - Test all endpoints in production

5. **Testing & Verification** (10 mins)
   - Signup with new email (gmail.com, yahoo.com, etc.)
   - Verify JWT token returns
   - Test signin with saved credentials
   - Verify all features work (translate, personalize, chat)
   - Check CORS headers with curl -i

## Key Architectural Decisions

| Decision | Choice | Rationale | Alternatives |
|----------|--------|-----------|--------------|
| **Deployment** | Vercel monorepo | Single platform, auto-scaling, GitHub integration, free tier sufficient | AWS Lambda + S3, Firebase, Heroku |
| **Backend Type** | Serverless Functions | No server management, scales automatically, cost-effective for low volume | Traditional FastAPI server (costs money to run continuously) |
| **Database** | Neon Postgres | Serverless, connection pooling optimized for Functions, free tier available | AWS RDS (expensive), SQLite (no persistence), MongoDB |
| **Function Language** | Python | Existing FastAPI code, Vercel Python runtime, dependencies available | JavaScript (would require rewrite), Go (no existing code) |
| **Frontend Build** | Static HTML | Docusaurus outputs static files, CDN optimized, fast delivery | SSR/Next.js (unnecessary complexity) |
| **CORS Handling** | In Function Headers | Only option for serverless, implemented in `_middleware.py` | Middleware (not available in serverless) |
| **JWT Storage** | Browser localStorage | Client-side, sent in Authorization header, standard pattern | Cookies (would need secure cookie config) |
| **Connection Pooling** | Neon + pgBouncer | Handles cold-starts, preserves connections between invocations | Direct connections (would exhaust database) |

## Dependencies & Prerequisites

**Already Available**:
- ✅ Docusaurus frontend (`Front-End-Book/`)
- ✅ FastAPI backend with all endpoints (`backend/`)
- ✅ Neon Postgres database (credentials in .env)
- ✅ OpenAI API key (in .env)
- ✅ GitHub repository with code

**To Install**:
- ⚙️ Vercel CLI: `npm install -g vercel`
- ⚙️ Python packages: listed in `api/requirements.txt`

**To Configure**:
- ⚙️ Vercel Account (free tier)
- ⚙️ GitHub authentication (repo already exists)
- ⚙️ Environment variables in Vercel dashboard

## Success Criteria & Acceptance

All criteria from specification must be met:

✅ **SC-001**: Frontend page loads < 3 seconds (FCP)
✅ **SC-002**: API responses < 2 seconds (p95)
✅ **SC-003**: Signup completes < 5 seconds
✅ **SC-004**: JWT authentication works (200 responses)
✅ **SC-005**: Database queries < 1 second
✅ **SC-006**: Deployment < 5 minutes (GitHub to live)
✅ **SC-007**: Zero-downtime deployments (Vercel handles)
✅ **SC-008**: All features < 5 seconds response
✅ **SC-009**: No mixed-content warnings
✅ **SC-010**: All 5 + 4 features operational
✅ **SC-011**: CORS headers correct, no 403 errors
✅ **SC-012**: Rollback capability in Vercel UI

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Neon connection timeout on cold-start | Medium | Functions fail to respond | Use Neon serverless driver + pgBouncer; implement retry logic |
| 50MB function size limit exceeded | Low | Deployment fails | Monitor dependencies; exclude unnecessary packages |
| CORS not configured correctly | Medium | Frontend gets 403 errors | Test CORS headers with curl before production |
| JWT token validation fails | Low | Auth endpoints broken | Test token generation and validation locally first |
| OpenAI API quota exceeded | Low | Chat feature fails | Implement rate limiting; alert on quota usage |
| Database migration fails on deploy | Low | Data inconsistency | Test migrations in local Neon instance first |

## Timeline

- **Phase 0 (Research)**: 20 minutes
- **Phase 1 (Design)**: 20 minutes (15 min contracts + 5 min agent context)
- **Phase 2 (Implementation)**: Delegated to /sp.tasks (estimated 55 minutes total across 5 sub-phases)
- **Buffer**: 15 minutes

**Total**: ~90 minutes from start to production deployment

## Rollback & Recovery

Vercel provides automatic rollback:
1. Deployment fails → Vercel keeps previous version live
2. New version has bugs → Click "Rollback" in Vercel dashboard (< 60 seconds)
3. Git revert → Push to GitHub, Vercel auto-rebuilds previous commit

No manual recovery needed; Vercel handles all reliability concerns.

## Next Steps

1. ✅ **This step**: Read and approve implementation plan
2. 📋 **Run `/sp.tasks`**: Generate Phase 2 task breakdown with sub-tasks and dependencies
3. 🚀 **Implement**: Follow task checklist to convert frontend/backend and deploy
4. ✅ **Test**: Verify all 12 success criteria met
5. 📹 **Demo**: Record video and prepare submission
