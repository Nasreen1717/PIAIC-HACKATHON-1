---
id: 002
title: Create Vercel deployment implementation plan
stage: plan
date: 2026-03-03
surface: agent
model: claude-haiku-4-5-20251001
feature: vercel-deployment
branch: 011-vercel-deployment
user: user
command: /sp.plan
labels: ["plan", "architecture", "serverless", "vercel", "deployment", "phase-1"]
links:
  spec: specs/011-vercel-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/011-vercel-deployment/plan.md
  - specs/011-vercel-deployment/research.md
  - specs/011-vercel-deployment/data-model.md
  - specs/011-vercel-deployment/quickstart.md
  - specs/011-vercel-deployment/contracts/auth.openapi.json
tests:
  - Phase 0: All unknowns resolved in research.md
  - Phase 1: Data model defined with 3 entities
  - Phase 1: API contracts documented (OpenAPI auth spec)
  - Phase 1: Quickstart guide covers local development
  - Constitution check: All 5 principles satisfied
---

## Prompt

Create complete implementation plan for Vercel deployment with serverless backend.

ARCHITECTURE:
Frontend: Docusaurus static site on Vercel
Backend: FastAPI converted to Vercel Serverless Functions in /api folder
Database: Neon Postgres with serverless driver
Structure: Monorepo with frontend and /api in same project

[Full technical context and detailed requirements provided in user input - 400+ lines]

## Response snapshot

Created comprehensive Phase 1 (Design & Contracts) implementation plan with 5 deliverables:

**1. plan.md** (140 lines)
- Summary: Deploy complete hackathon to Vercel monorepo with static frontend + serverless backend
- Technical Context: Python 3.9+, FastAPI, Neon Postgres, Vercel Functions, <3s FCP, <2s API latency
- Constitution Check: ✅ All 5 principles satisfied (accuracy, code quality, spec-driven, modular, safety)
- Project Structure: Monorepo layout (Front-End-Book/ + api/ + vercel.json)
- 5 Implementation Phases: Research (20m) → Design (20m) → Tasks (deferred to /sp.tasks) → Implementation → Deployment
- 7 Key Architectural Decisions with rationale and alternatives:
  * Neon serverless driver + asyncpg (vs psycopg2 + traditional pooling)
  * CORS in _middleware.py (vs missing middleware)
  * Vercel Handler pattern (vs ASGI Mangum wrapper)
  * Build-time env vars (vs runtime config)
  * localStorage for JWT (vs cookies/memory)
  * Pinned dependencies (vs floating versions)
  * Wildcard API routing (vs explicit routes)
- Risks & Mitigation: Cold-starts, 50MB limits, CORS errors, token validation, quota exceeded
- Timeline: 90 minutes total
- Rollback strategy: Vercel auto-rollback and manual rollback via UI

**2. research.md** (280 lines)
- 7 Technology Decisions resolved:
  1. **Neon serverless driver** for connection pooling (asyncpg + pgBouncer) - solves cold-start exhaustion
  2. **Custom CORS in _middleware.py** - only option for Vercel Functions
  3. **Vercel Handler pattern** over ASGI - faster cold-start, smaller size, direct code
  4. **Build-time env vars** - faster load, simpler config
  5. **localStorage JWT** - standard pattern for serverless API
  6. **Pinned dependency versions** - reproducibility, 50MB limit adherence
  7. **Wildcard API routing** - auto-routes new functions, less maintenance
- Technology Stack Table: Vercel, Docusaurus, Python 3.9, FastAPI 0.104.1, Neon, asyncpg, PyJWT 2.8.1, passlib 1.7.4, OpenAI SDK 1.3.9
- Best practices: Connection pooling, cold-start optimization, CORS centralization, version pinning, error handling, logging, security
- Conclusion: All unknowns resolved, ready for Phase 1 Design

**3. data-model.md** (360 lines)
- 3 Main Entities:
  * **User** (8 columns): id, email (unique), password_hash, full_name, is_active, created_at, updated_at + indexes
  * **UserBackground** (9 columns): id, user_id (FK), software_background, hardware_background, ros_experience, python_level, learning_goal, available_hardware, timestamps
  * **ConversationHistory** (7 columns): id, user_id (FK), conversation_id (UUID), role (user/assistant), message, tokens_used, created_at
- Relationships: 1:1 (User↔Background), 1:N (User→ConversationHistory)
- Validation Rules: Email format + unique, password bcrypt, enums for background fields, JWT validation
- State Transitions: User auth flow (signup→token→protected access), logout flow (delete token→redirect)
- Schema Creation: Complete SQL CREATE TABLE statements with indexes and constraints
- Performance: Query patterns and estimated times (<10ms email lookup, <50ms conversation fetch)
- Security: Bcrypt hash, foreign keys, JWT secret, no plaintext, HTTPS enforced
- Migration strategy: Idempotent schema creation on cold-start

**4. contracts/auth.openapi.json** (150 lines)
- OpenAPI 3.0 spec for authentication endpoints
- Endpoints:
  * POST /api/auth/signup: Any email allowed, password validation (6+ chars, 1 letter + 1 number), optional background fields
  * POST /api/auth/signin: Email + password, optional remember_me flag
- Responses: TokenResponse (access_token, token_type, expires_in), ErrorResponse (detail)
- Schemas: Full request/response definitions with examples
- Security: bearerAuth scheme for protected endpoints

**5. quickstart.md** (350 lines)
- Prerequisites: Node 18+, Python 3.9+, Vercel CLI, .env.local file
- Setup: npm install, pip install -r requirements.txt, create .env.local
- Local Development: `vercel dev` to emulate Vercel Functions locally
- Testing:
  * Signup: curl with any email (gmail, yahoo, etc.) → receives JWT token
  * Signin: curl with saved credentials → receives JWT token
  * Protected endpoints: curl with Authorization: Bearer header
  * CORS: curl -i to verify headers
  * Frontend: Navigate to localhost:3000, test signup flow
- Debugging: Logs from vercel dev, database direct connection, env var checks
- Production Build: `npm run build` for static artifacts
- Git Workflow: Feature branch → PR → merge to main → Vercel auto-deploy
- Common Issues: Module imports, DB timeout, CORS errors, 401 unauthorized with solutions

## Outcome

- ✅ Impact: Complete Phase 1 (Design & Contracts) deliverables enable Phase 2 (Implementation tasks)
- 🧪 Tests: Constitution check passed, all unknowns resolved, monorepo structure validated
- 📁 Files: 5 new artifacts (plan.md, research.md, data-model.md, quickstart.md, auth.openapi.json)
- 🔁 Next prompts: `/sp.tasks` to generate Phase 2 task breakdown; then implementation
- 🧠 Reflection: Plan is comprehensive, actionable, and follows spec exactly. 7 key decisions documented with rationale. Local dev workflow clear. Ready for task generation.

## Evaluation notes (flywheel)

- Failure modes observed: None - all phases complete and integrated
- Graders run and results (PASS/FAIL): Constitution check PASS (5/5 principles), Technical context complete, Decisions documented
- Prompt variant (if applicable): None
- Next experiment: Run `/sp.tasks` to generate granular implementation tasks with dependencies and acceptance criteria
