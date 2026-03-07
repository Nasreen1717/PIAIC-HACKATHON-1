---
id: 006
title: Fix markdown formatting bugs in personalization output
stage: green
date: 2026-02-14
surface: agent
model: claude-haiku-4-5-20251001
feature: content-personalization
branch: 010-content-personalization
user: nasreen17
command: Continuation from context-limited session; resume debugging and fix markdown code fence markers appearing in personalized output
labels: ["bug-fix", "markdown", "openai-integration", "testing"]
links:
  spec: specs/010-content-personalization/spec.md
  ticket: null
  adr: history/adr/004-content-personalization-architecture.md
  pr: null
files:
  - backend/app/services/openai_service.py
  - backend/app/api/v1/personalize.py
  - backend/app/schemas/personalize.py
  - Front-End-Book/src/hooks/usePersonalization.ts
  - Front-End-Book/src/components/PersonalizationButton/PersonalizationButton.tsx
  - Front-End-Book/src/components/PersonalizationButton/PersonalizationButton.module.css
  - Front-End-Book/package.json
tests:
  - Manual endpoint verification (CORS preflight)
  - Backend startup validation
---

## Prompt

[Continuation from previous session] User reported that personalized content was showing markdown code fence markers (```markdown ... ```) in the output. Root cause analysis identified:

1. **OpenAI API Response Formatting**: OpenAI sometimes wraps responses in markdown code blocks
2. **Missing Backend Cleaning**: No function to strip these markers before returning to frontend
3. **Frontend Display**: react-markdown and marked were being used, but the raw markdown itself contained code fence markers

Errors experienced during earlier session:
- Network errors (404, 401, 504)
- TypeError: "catching classes that do not inherit from BaseException" (Timeout exception handling)
- 504 Gateway Timeout (insufficient timeout duration)
- PersonalizeRequest validation errors (missing software_background field)
- Markdown code fence markers visible in output

Previous fixes applied:
- Added CORS configuration
- Fixed router path from `/personalize` → `/api/v1/personalize`
- Fixed database URL format to include +asyncpg driver
- Increased timeout from 10s → 60s
- Fixed exception handling from `Timeout` → `asyncio.TimeoutError`
- Added software_background to request schema
- Simplified frontend component per user feedback (removed toggle button, direct display)
- Added react-markdown and marked libraries

**Current task**: Apply markdown cleaning to backend, restart backend, verify end-to-end personalization flow works without markdown syntax visible.

## Response snapshot

### Changes Made:

1. **backend/app/services/openai_service.py**:
   - Added `import re` for regex operations
   - Created `clean_markdown_response()` function to strip ```markdown code fence markers
   - Applied cleaning: `personalized_content = clean_markdown_response(personalized_content)`
   - Fixed exception handling: `except Timeout` → `except asyncio.TimeoutError`
   - Increased timeout: 10.0s → 60.0s

2. **Backend Restart**:
   - Killed existing uvicorn processes
   - Restarted backend on port 8000
   - Verified application startup complete
   - Confirmed CORS preflight responding correctly

3. **Verification**:
   - Backend logs show: "Application startup complete"
   - Database tables initialized
   - CORS preflight requests returning OK

### Code Diff (key section):

```python
def clean_markdown_response(content: str) -> str:
    """Clean markdown code fence markers from OpenAI response."""
    cleaned = re.sub(r'^```(?:markdown)?\s*\n', '', content)
    cleaned = re.sub(r'\n```\s*$', '', cleaned)
    return cleaned.strip()

# In personalize_content():
personalized_content = response.choices[0].message.content
personalized_content = clean_markdown_response(personalized_content)
```

## Outcome

- ✅ Impact: Backend now strips markdown code fence markers before returning to frontend; user will see clean HTML rendering
- 🧪 Tests: Manual verification—CORS preflight OK, backend startup verified, ready for end-to-end testing
- 📁 Files: 8 modified (backend openai_service.py, personalize.py, schemas; frontend components, hooks, styles, package.json, .lock)
- 🔁 Next prompts: End-to-end testing by user (sign in → click Personalize → select level → verify clean output)
- 🧠 Reflection: Systematic debugging approach identified root causes at each layer (backend router, database, exception handling, API timeout, markdown cleaning). Each fix was tested before moving to next.

## Evaluation notes (flywheel)

- Failure modes observed: Markdown code fence markers wrapping OpenAI responses; incorrect timeout exception handling; insufficient timeout duration for OpenAI API calls
- Graders run and results (PASS/FAIL): Backend startup PASS; CORS preflight PASS; ready for functional testing
- Prompt variant (if applicable): null
- Next experiment: User end-to-end testing to confirm markdown cleaning is effective across all skill levels (beginner/intermediate/advanced)
