---
id: 002
title: Create Implementation Plan
stage: plan
date: 2026-02-10
surface: agent
model: claude-haiku-4-5
feature: 009-translation-protection
branch: 008-navbar-auth (context) → 009-translation-protection (target)
user: nasreen17
command: /sp.plan
labels: ["plan", "architecture", "authentication", "api-design", "translation"]
links:
  spec: /mnt/d/code/Hackathon-1/specs/009-translation-protection/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /mnt/d/code/Hackathon-1/specs/009-translation-protection/plan.md
  - /mnt/d/code/Hackathon-1/specs/009-translation-protection/research.md
  - /mnt/d/code/Hackathon-1/specs/009-translation-protection/data-model.md
  - /mnt/d/code/Hackathon-1/specs/009-translation-protection/contracts/translate-api.openapi.json
  - /mnt/d/code/Hackathon-1/specs/009-translation-protection/quickstart.md
tests:
  - Constitution Check: PASS (5/5 principles satisfied)
  - All research unknowns resolved: PASS (6 decisions documented)
  - Data model complete: PASS (4 entities, 3 DTOs, state flows documented)
  - API contract valid: PASS (OpenAPI 3.0.0 schema with examples)
---

## Prompt

```
/sp.plan translation-protection-spec.md

Create implementation plan for: Translation Protection with Authentication

Based on specification: translation-protection-spec.md

Architecture Decisions Needed:
1. Auth Check Location: Component level vs Route level vs API level
2. Error Handling: Toast notifications vs inline messages vs modal
3. Token Storage: localStorage vs cookies (already decided by better-auth)
4. Backend Middleware: FastAPI dependency vs decorator

Tech Stack:
- Frontend: React, TypeScript, Docusaurus, existing AuthContext
- Backend: FastAPI, python-jose (JWT), existing auth middleware
- State Management: React hooks (useState, useEffect)

[... detailed context provided by user ...]
```

## Response snapshot

Created comprehensive implementation plan for Translation Protection with Authentication feature:

**Phase 0: Research Complete**
- ✅ 6 architectural decisions documented and verified against codebase
- ✅ 0 unknowns remain (no NEEDS CLARIFICATION markers)
- ✅ All decisions grounded in existing patterns (ProtectedFeature, get_current_user)

**Phase 1: Design Artifacts Generated**
- ✅ research.md: Decision records with alternatives and rationale
- ✅ data-model.md: Entities (User, TranslateRequest, TranslateResponse), state flows, validation rules
- ✅ contracts/translate-api.openapi.json: Complete OpenAPI 3.0.0 specification with examples
- ✅ quickstart.md: Step-by-step integration guide for frontend and backend

**Key Architectural Decisions**:

1. **Frontend Protection**: Use existing ProtectedFeature wrapper (already applied in TranslationButton)
   - Shows authentication prompt to logged-out users
   - Shows translation button to authenticated users
   - No changes needed (pattern already in place)

2. **Backend Protection**: Reuse get_current_user FastAPI dependency from auth.py
   - Extracts JWT from Authorization header
   - Validates token signature and expiration
   - Handles 401 responses for missing/invalid tokens
   - Proven pattern in auth routes

3. **API Endpoint**: Create new /api/v1/translate router following existing chat.py pattern
   - Consistent with API structure
   - Separate module for translation logic
   - Follows v1 versioning scheme

4. **Error Responses**: Match existing auth error format ({"detail": "..."})
   - Clear to frontend
   - No sensitive token information exposed
   - Consistent with HTTP/REST conventions

5. **Token Transmission**: Authorization header from useAuth hook (existing pattern)
   - Standard HTTP bearer token approach
   - Token already available via AuthContext

6. **Token Expiration**: Frontend detects 401 response, clears auth state
   - Already handled in AuthContext for other API calls
   - Reuse existing pattern for consistency

**Constitution Compliance**: ✅ PASS
- ✅ Technical Accuracy: Uses proven FastAPI patterns, no new external dependencies
- ✅ Hands-On Learning: Includes concrete code examples and acceptance criteria
- ✅ Spec-Driven Development: Complete spec→plan→tasks workflow
- ✅ Modular Progressive: Feature isolated, doesn't break existing modules
- ✅ Safety First: Defense-in-depth (frontend UX + backend validation)

**Project Structure**:
- Frontend: Minimal changes (mostly verification of existing patterns)
- Backend: New router at app/api/v1/translate.py + schemas/translate.py
- No database schema changes required
- No new dependencies needed

## Outcome

- ✅ Impact: Complete architectural design ready for task generation; all design decisions documented with rationale and alternatives
- 🧪 Tests: Constitution Check PASS; 6 decision records with verification
- 📁 Files: 5 Phase 1 artifacts created (plan, research, data-model, contracts, quickstart)
- 🔁 Next prompts: `/sp.tasks` to generate implementation tasks; `/sp.adr` to document JWT dependency injection decision (optional)
- 🧠 Reflection: Key insight: frontend protection already implemented via ProtectedFeature wrapper. Planning identified this early, allowing focus on backend JWT validation. No surprises or blocked dependencies discovered during design phase.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan completed without blockers; all unknowns resolved through code review
- Graders run and results (PASS/FAIL): Constitution Check PASS; Research Complete PASS; Design Quality PASS
- Prompt variant (if applicable): Standard plan generation with architectural decision focus
- Next experiment (smallest change to try): Execute `/sp.tasks` to break plan into actionable, testable tasks; verify task dependencies align with implementation phases

---

**Status**: Phase 1 design complete; ready for Phase 2 task generation
**Ready for**: `/sp.tasks` command to generate tasks.md
**Timeline**: 30-minute implementation feasible based on design
**Confidence Level**: HIGH (all patterns proven, no experimental code)
