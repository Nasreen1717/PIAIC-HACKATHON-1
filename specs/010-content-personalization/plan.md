# Implementation Plan: Content Personalization Based on User Background

**Feature Branch**: `010-content-personalization`
**Created**: 2026-02-11
**Status**: Ready for Implementation
**Specification**: [spec.md](./spec.md)

---

## Executive Summary

This plan outlines the implementation strategy for the Content Personalization feature—a OpenAI-powered system that adapts chapter content to users' technical skill levels (beginner/intermediate/advanced) while preserving all citations, code examples, and technical facts.

**Estimated Total Effort**: 2.5-3 hours (including testing)
**Phases**: 4 sequential phases + 1 research phase
**Risk Level**: Low (pattern reuse from translation feature; clear requirements)

---

## Architecture Overview

### High-Level Flow

```
User clicks "Personalize for Me" (frontend)
         ↓
usePersonalization hook fetches article content
         ↓
POST /api/v1/personalize with content + JWT token
         ↓
Backend validates JWT, extracts user profile
         ↓
OpenAI API transforms content based on user level
         ↓
Response with personalized markdown
         ↓
Frontend replaces DOM content, shows "Reset to Original"
         ↓
User can click "Reset to Original" to restore original
```

### System Components

**Frontend**:
- `PersonalizationButton` component (states: default, loading, personalized, error)
- `usePersonalization` hook (API calls, debouncing)
- Button placed at article start (using ProtectedFeature wrapper)

**Backend**:
- `POST /api/v1/personalize` endpoint
- `OpenAIService` for prompt generation (3 templates: beginner/intermediate/advanced)
- Pydantic schemas for request/response validation

**Data Flow**:
- No database changes (user profile from JWT token)
- Content in-memory (original preserved, personalized generated on-demand)

---

## Key Architectural Decisions (ADR Required)

### ADR-001: Content Extraction Method

**Decision**: Read from DOM (client-side), not server API

**Rationale**:
- Docusaurus is static site; chapter content available in DOM
- No extra round-trip to fetch content from server
- Same pattern as translation feature (proven working)
- Reduces backend load

**Alternatives**:
- Option B (Fetch from API): Would require additional backend endpoint; slower
- Option A (DOM): Selected for simplicity and consistency

**Implementation**: `document.querySelector('article')?.innerHTML` at button click

---

### ADR-002: State Management

**Decision**: Component state (useState) for PersonalizationButton; Context API for sharing across pages not needed at MVP

**Rationale**:
- Personalization is localized to single article/chapter
- No need to share state across multiple components
- Component state keeps implementation simple
- Matches translation feature pattern

**Alternatives**:
- Option B (Context API): Overkill for localized state; adds complexity
- Option C (React Query): Unnecessary for read-only transformations
- Option A (useState): Selected for simplicity

**Implementation**:
```typescript
const [state, setState] = useState<'default' | 'loading' | 'personalized' | 'error'>('default');
const [error, setError] = useState<string | null>(null);
const [personalizationLevel, setPersonalizationLevel] = useState<string | null>(null);
```

---

### ADR-003: OpenAI Prompt Strategy

**Decision**: Three dedicated prompt templates (beginner/intermediate/advanced) with explicit constraints

**Rationale**:
- Ensures consistent, predictable output for each level
- Explicit "preserve citations, code, facts" prevents hallucination
- Level-specific instructions (readability grade, tone, emphasis) improve quality
- Constitutional requirements encoded in system prompt

**Prompt Template Structure**:

**Beginner Template**:
```
System: You are a professional educator. Transform technical content for beginners.
PRESERVE EXACTLY:
- All IEEE citations (format: [N], [Author Year])
- All code examples (line-by-line, no changes)
- All version numbers, APIs, safety protocols
- All learning objectives

TRANSFORM:
- Reading level: Flesch-Kincaid 12-14
- Language: Simple, everyday terms; explain technical jargon
- Structure: Numbered lists, step-by-step
- Add: 💡 Tip boxes, ⚠️ Common Mistakes, glossary links, analogies
- Code comments: Detailed, explain logic
- Hardware: Cloud/simulation-first (no GPU required)
- Tone: Encouraging, supportive

Content to transform: [CONTENT]
```

**Intermediate Template**:
```
System: You are a professional technical writer. Maintain balanced technical content.
PRESERVE EXACTLY:
- All IEEE citations
- All code examples
- All version numbers, APIs, safety protocols

TRANSFORM:
- Language: Technical with brief explanations
- Structure: Standard paragraphs with callouts
- Add: Best practices, optimization tips
- Code comments: Moderate, explain patterns
- Hardware: Balance simulation and hardware deployment
- Tone: Professional, educational

Content to transform: [CONTENT]
```

**Advanced Template**:
```
System: You are a senior technical researcher. Optimize for expert readers.
PRESERVE EXACTLY:
- All IEEE citations (highlight seminal papers)
- All code examples
- All version numbers, APIs, safety protocols
- All performance metrics

TRANSFORM:
- Language: Professional terminology, assume CS/robotics background
- Structure: Concise, information-dense
- Add: Performance optimization tips, benchmarks, advanced use cases, research applications
- Code comments: Minimal, focus on complex patterns
- Hardware: RTX/Jetson deployment, CUDA optimization
- Tone: Technical, research-focused

Content to transform: [CONTENT]
```

**Hardware & Goal Context** (appended to all prompts):
```
Additional context:
- User hardware background: {user.hardware_background} (none/basic/advanced)
- User learning goal: {user.learning_goal} (career/hobby/research)

Apply these adjustments:
- Hardware=none: Emphasize cloud options (Isaac Cloud, AWS RoboMaker)
- Hardware=basic: Simulation-first (Gazebo, Isaac Sim), mention GPU path
- Hardware=advanced: RTX/Jetson deployment, CUDA optimization
- Goal=career: Industry relevance, job market skills
- Goal=hobby: Fun, creative applications
- Goal=research: Novel approaches, state-of-the-art techniques
```

---

### ADR-004: Error Handling Strategy

**Decision**: Graceful degradation with user-friendly fallbacks

**Error Scenarios**:

| Error | Cause | Response | User Action |
|-------|-------|----------|-------------|
| OpenAI timeout (>10s) | API slow/unavailable | Show original + "Service unavailable" error | Click "Reset" or retry |
| OpenAI rate limit | Too many requests | Queue request or show "Please try again in N seconds" | Wait + retry |
| Invalid JWT | Expired/missing token | Redirect to signin with message | Sign in again |
| Empty content | No article found | Show "No content found" error | N/A |
| Network error | Connection lost | Show "Network error" + fallback to original | Retry |
| Invalid response | Malformed OpenAI response | Show "Transformation failed" + original | Retry |

**Implementation**:
```typescript
try {
  const response = await fetch('/api/v1/personalize', { /* ... */ });
  if (response.status === 401) {
    // Redirect to signin
    history.push('/signin');
  } else if (response.status === 429) {
    // Show retry message
    setError('Rate limited. Please try again in a moment.');
  } else if (!response.ok) {
    // Show user-friendly error
    const data = await response.json();
    setError(data.detail || 'Personalization failed. Please try again.');
  }
  // ... success case
} catch (err) {
  // Network error
  setError('Network error. Please check your connection.');
}
```

---

### ADR-005: Mobile Responsiveness

**Decision**: Inline button (not fixed); full content replacement (not expandable)

**Rationale**:
- Inline button integrates naturally with chapter layout
- Full replacement provides complete personalized experience on mobile
- Consistent with desktop UX
- "Reset to Original" provides exit path on all screen sizes

**Implementation**:
- Button: 100% touch-friendly (44px min height, adequate padding)
- CSS: `@media (max-width: 768px) { ... }` for responsive sizing
- Content: Replace in-place (no scrolling surprises)
- States: All states remain visible on mobile

---

## Constitutional Alignment Check

### Progressive Learning Architecture ✅

- **BEGINNER**: Flesch-Kincaid 12-14 (spec requirement), simple language, step-by-step (FR-022)
- **INTERMEDIATE**: Balanced technical, standard flow (FR-023)
- **ADVANCED**: Information-dense, research-focused (FR-024)
- **Implementation**: Three distinct prompt templates encode these requirements

### Content Integrity ✅

- **Citations**: MUST preserve all IEEE citations (FR-016, prompt templates)
- **Code**: MUST preserve all code examples exactly (FR-017, prompt templates)
- **Facts**: MUST preserve technical accuracy, version numbers, APIs (FR-018, FR-020)
- **Implementation**: System prompt explicitly enforces preservation with "PRESERVE EXACTLY" sections

### Accessibility & Inclusion ✅

- **Cloud Options**: Beginners get cloud/simulation first; no GPU required (FR-022)
- **Hardware Context**: Three hardware levels (none/basic/advanced) with appropriate guidance (FR-025)
- **Learning Goals**: Three learning goals (career/hobby/research) with tone adjustments (FR-026)
- **Implementation**: Hardware and goal context appended to all prompts

### Feature Protection ✅

- **Authentication**: Endpoint requires valid JWT token (FR-010, FR-020)
- **Authorization**: Frontend uses ProtectedFeature wrapper (FR-009)
- **Profile Data**: User background retrieved from JWT token context (FR-027)
- **Implementation**: Existing `get_current_user` dependency enforces auth

---

## Phase 0: Research & Preparation

### Research Tasks

1. **OpenAI API Integration Pattern**
   - Task: Verify gpt-4o-mini model availability and pricing
   - Rationale: Confirm cost-effective model selection
   - Finding: Model confirmed in backend config (requirements.txt has openai==1.14.0)

2. **Docusaurus Article Content Structure**
   - Task: Verify article DOM structure for content extraction
   - Rationale: Ensure `document.querySelector('article')` reliably finds content
   - Finding: Docusaurus uses `<article>` wrapper for chapter content; queryable via DOM

3. **JWT Token Handling in Frontend**
   - Task: Verify useAuth hook provides user profile (software_background, hardware_background, learning_goal)
   - Rationale: Ensure user profile available at component level
   - Finding: AuthContext stores full user profile; useAuth hook exposes it

4. **OpenAI Rate Limiting**
   - Task: Understand rate limit handling for typical chat API calls
   - Rationale: Design appropriate error handling
   - Finding: gpt-4o-mini has generous rate limits for typical use; implement 429 handling + user message

### Findings Summary

✅ All critical unknowns resolved:
- OpenAI integration ready (SDK in requirements, config.py has API key)
- Docusaurus content structure confirmed
- User profile data available via existing hooks
- Error handling patterns established

**Status**: Ready for Phase 1 Design

---

## Phase 1: Backend Foundation

### 1.1 Create `backend/app/schemas/personalize.py`

**Pydantic Models**:

```python
class PersonalizeRequest(BaseModel):
    """Request to personalize article content"""
    content: str = Field(..., min_length=1, max_length=50000, description="Article content to personalize")
    hardware_background: Literal["none", "basic", "advanced"] = Field(...)
    learning_goal: Literal["career", "hobby", "research"] = Field(...)

class PersonalizeResponse(BaseModel):
    """Response with personalized content"""
    personalized_content: str = Field(..., description="Personalized markdown content")
    personalization_level: Literal["beginner", "intermediate", "advanced"] = Field(...)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata (time, tokens)")
```

**Files Modified**: NEW FILE

### 1.2 Create `backend/app/services/openai_service.py`

**Functions**:

```python
async def generate_personalization_prompt(
    content: str,
    level: Literal["beginner", "intermediate", "advanced"],
    hardware_background: str,
    learning_goal: str
) -> str:
    """Generate OpenAI system + user prompt for personalization"""
    # Returns prompt text with embedded content

async def personalize_content(
    content: str,
    software_background: str,  # Maps to level
    hardware_background: str,
    learning_goal: str
) -> Tuple[str, Dict[str, Any]]:
    """Call OpenAI API and return personalized content + metadata"""
    # Returns (personalized_content, {time_ms, tokens_used})
```

**Error Handling**: Timeouts, rate limits, API errors (see ADR-004)

**Files Modified**: NEW FILE

### 1.3 Create `backend/app/api/v1/personalize.py`

**Endpoint**:

```python
@router.post("/personalize", response_model=PersonalizeResponse)
async def personalize(
    request: PersonalizeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PersonalizeResponse:
    """Personalize article content based on user's background"""
    # 1. Validate request (already done by Pydantic)
    # 2. Get user's actual software_background from current_user (validate matches hardware_background, learning_goal?)
    # 3. Call openai_service.personalize_content()
    # 4. Return PersonalizeResponse
    # 5. Handle errors per ADR-004
```

**Status Codes**:
- 200: Success
- 400: Invalid content (empty, too long)
- 401: Invalid/missing JWT
- 429: Rate limited (retry-after)
- 500: OpenAI API error

**Files Modified**: NEW FILE

### 1.4 Update `backend/app/main.py`

**Change**: Register personalize router

```python
from app.api.v1 import personalize
app.include_router(personalize.router)
```

**Files Modified**: EXISTING FILE (1 line addition)

### 1.5 Testing - Phase 1

**Test Cases**:
1. Beginner personalization: Send article + software_background="beginner" → Check reading level
2. Advanced personalization: Send article + software_background="advanced" → Check technical density
3. Hardware context: Send different hardware_background values → Verify cloud/simulation/deployment emphasis
4. Error handling: Invalid JWT → 401, Empty content → 400, OpenAI timeout → 500
5. Citation preservation: Check all citations remain unchanged in response
6. Code preservation: Check all code blocks remain unchanged in response

**Testing Tool**: curl with JWT token

```bash
curl -X POST http://localhost:8000/api/v1/personalize \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "...",
    "hardware_background": "basic",
    "learning_goal": "career"
  }'
```

---

## Phase 2: Frontend Component

### 2.1 Create `src/components/PersonalizationButton/PersonalizationButton.tsx`

**Component States**:
- **default**: "Personalize for Me" button visible
- **loading**: Spinner + "Personalizing..." message
- **personalized**: "Personalized for: [Level]" indicator + "Reset to Original" button
- **error**: Error message + retry option

**Key Features**:
- ProtectedFeature wrapper (only visible if authenticated)
- Debounce rapid clicks (300ms)
- Store original content in ref
- Smooth state transitions via CSS animations

**Props**: None (all from hooks)

**Hooks Used**:
- `useAuth()`: Get user profile (software_background, hardware_background, learning_goal)
- `usePersonalization()`: API calls + state management

**Files Created**: NEW FILE

### 2.2 Create `src/components/PersonalizationButton/PersonalizationButton.module.css`

**Styles**:
- Button: 44px min height, adequate padding, touch-friendly
- Loading spinner: CSS animation (rotate 360° over 1s)
- Error message: Red text, readable
- Mobile responsive: `@media (max-width: 768px) { ... }`
- State transitions: CSS fade/slide animations (0.3s)

**Files Created**: NEW FILE

### 2.3 Create `src/hooks/usePersonalization.ts`

**Functionality**:
```typescript
function usePersonalization() {
  const { user, token } = useAuth();
  const [state, setState] = useState<'default' | 'loading' | 'personalized' | 'error'>('default');
  const [error, setError] = useState<string | null>(null);
  const [personalizationLevel, setPersonalizationLevel] = useState<string | null>(null);
  const originalContentRef = useRef<string>('');

  const personalize = useCallback(async () => {
    // 1. Get article content from DOM
    // 2. POST to /api/v1/personalize with user profile
    // 3. Handle response: replace content, update state
    // 4. Handle errors: show message, revert state
  }, [user, token]);

  const resetToOriginal = useCallback(() => {
    // 1. Restore original content
    // 2. Reset state to 'default'
  }, []);

  return { state, error, personalizationLevel, personalize, resetToOriginal };
}
```

**Error Handling**: Per ADR-004, user-friendly messages

**Files Created**: NEW FILE

### 2.4 Testing - Phase 2

**Test Cases**:
1. Component renders with "Personalize for Me" button when authenticated
2. Component doesn't render when not authenticated (ProtectedFeature wrapper)
3. Clicking button shows loading spinner
4. After API response, content is replaced and state is "personalized"
5. "Reset to Original" button restores exact original
6. Error message displays on API failure
7. Mobile responsiveness: button visible and clickable on small screens
8. Rapid clicks are debounced (only one request sent)

**Testing Tool**: React Testing Library / Storybook

---

## Phase 3: Integration

### 3.1 Add Button to Docusaurus Chapter Layout

**Location**: At start of article, after metadata but before main heading

**Implementation**: Swizzle or add to existing DocItem component

**Approach**:
- If DocItem already swizzled → Add PersonalizationButton before children
- If not swizzled → Create wrapper component that imports original + adds button

**Files Modified**: `src/theme/DocItem/Layout/index.tsx` (or similar)

### 3.2 Wire Up Content Display Logic

**In PersonalizationButton**:
1. Fetch article content from `document.querySelector('article')`
2. Send to backend with user profile
3. Receive personalized content
4. Replace article DOM: `article.innerHTML = personalized_content`
5. Show "Reset to Original" button

**In Reset Logic**:
1. Restore original content: `article.innerHTML = originalContentRef.current`
2. Show "Personalize for Me" button

**Error Handling**: Per ADR-004

**Files Modified**: PersonalizationButton.tsx (existing)

### 3.3 Auth Protection

**Frontend**: ProtectedFeature wrapper ensures button only shows when authenticated

**Backend**: JWT validation via `get_current_user` dependency ensures endpoint protected

**Testing**: Try to call endpoint without JWT → 401 response

### 3.4 Integration Testing

**Test Cases**:
1. Full flow: Sign in → Click "Personalize for Me" → Content personalized → See "Reset to Original"
2. Reset flow: Click "Reset to Original" → Original content restored
3. Auth protection: Unauthenticated users don't see button
4. Profile data: Beginner user sees beginner content, advanced sees advanced
5. Hardware context: Choices affect content (cloud vs hardware emphasis)
6. Multiple chapters: Works independently on each chapter

---

## Phase 4: Testing & Polish

### 4.1 Beginner Personalization Validation

**Test**: Sign in as beginner user, click "Personalize for Me" on technical chapter

**Verification**:
- ✓ Reading level is Flesch-Kincaid 12-14 (use automated readability scorer)
- ✓ Language uses simple terms, explains jargon
- ✓ Has "💡 Tip" and "⚠️ Common Mistake" boxes
- ✓ Cloud/simulation emphasized over hardware
- ✓ All citations preserved exactly
- ✓ All code examples work unchanged
- ✓ All technical facts are correct

### 4.2 Advanced Personalization Validation

**Test**: Sign in as advanced/research user, click "Personalize for Me"

**Verification**:
- ✓ Content is concise and technical
- ✓ Assumes CS/robotics background
- ✓ Includes optimization tips and benchmarks
- ✓ Research papers from citations highlighted
- ✓ All citations preserved exactly
- ✓ All code examples work unchanged
- ✓ All technical facts are correct
- ✓ Hardware deployment emphasis (RTX/Jetson)

### 4.3 Hardware Variants Validation

**Test**: Personalize content for each hardware context (none/basic/advanced)

**Verification**:
- ✓ Hardware=none: Cloud options (Isaac Cloud, AWS) appear
- ✓ Hardware=basic: Simulation tools (Gazebo, Isaac Sim) emphasized
- ✓ Hardware=advanced: Hardware deployment and CUDA optimization appear

### 4.4 Mobile Responsiveness

**Test**: Open on mobile device (iOS Safari, Android Chrome)

**Verification**:
- ✓ Button is visible and clickable (44px min height)
- ✓ Loading spinner displays correctly
- ✓ Personalized content readable on small screen
- ✓ "Reset to Original" button is accessible
- ✓ No horizontal scrolling required

### 4.5 Error Scenario Testing

**Test Cases**:
1. OpenAI timeout: Endpoint takes > 10s → Show error message, original content intact
2. Invalid JWT: Call endpoint with expired token → 401 redirect to signin
3. Network error: Simulate connection loss → Show network error message
4. Empty content: No article on page → Show appropriate error
5. Rate limit: Rapid personalization requests → Queue or show retry message

### 4.6 Performance Verification

**Metrics**:
- ✓ Full personalization completes in < 8 seconds
- ✓ UI state transitions complete in < 200ms
- ✓ Content replacement is instant (no flicker)
- ✓ Mobile performance acceptable (no jank)

---

## File Structure

### Frontend (New Files)

```
src/components/PersonalizationButton/
├── PersonalizationButton.tsx          (React component, ~150 LOC)
├── PersonalizationButton.module.css   (Styles, ~100 LOC)
├── index.ts                           (Export)
└── __tests__/
    └── PersonalizationButton.test.tsx (Unit tests)

src/hooks/
└── usePersonalization.ts              (API hook, ~100 LOC)
```

### Backend (New Files)

```
backend/app/api/v1/
├── personalize.py                     (Endpoint, ~80 LOC)
└── schemas/
    └── personalize.py                 (Pydantic models, ~30 LOC)

backend/app/services/
└── openai_service.py                  (OpenAI integration, ~150 LOC)
```

### Backend (Modified Files)

```
backend/app/main.py                    (Add router registration, +2 lines)
```

### Integration (Modified Files)

```
src/theme/DocItem/Layout/index.tsx     (Add PersonalizationButton, +3-5 lines)
```

---

## Risk Analysis & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|-----------|
| OpenAI API timeout | Feature unusable | Medium | Implement 8s timeout + user-friendly error message |
| Citation preservation fails | Constitutional violation | Low | Explicit "PRESERVE EXACTLY" in prompt + validation |
| Code example modification | Constitutional violation | Low | Explicit code preservation in prompt + manual verification |
| Mobile UI broken | Poor UX on 50% devices | Low | Responsive design, test on actual devices |
| Rate limiting issues | User frustration | Low | Handle 429 status, show retry message + queue |
| Auth protection bypass | Security issue | Very Low | Rely on existing `get_current_user` dependency |

**Mitigation Summary**: Strong prompt engineering prevents content corruption; timeout/error handling prevents service unavailability; responsive design ensures mobile UX

---

## Success Criteria (from Specification)

✅ All measurable outcomes achievable:
- **SC-001**: Response time < 8 seconds → OpenAI API SLA + network latency
- **SC-002**: Citation preservation 100% → Explicit "PRESERVE EXACTLY" in prompt
- **SC-003**: Code preservation 100% → Explicit code preservation in prompt
- **SC-004**: Reading level Flesch-Kincaid 12-14 → Beginner prompt specifies this
- **SC-005**: Personalization works for all 3 levels → 3 distinct prompts
- **SC-006**: State transitions < 200ms → CSS animations only
- **SC-007**: 95% success rate → Error handling per ADR-004
- **SC-008**: Mobile responsive → CSS media queries
- **SC-009**: Instant reset → DOM restoration from ref
- **SC-010**: Hardware-aware personalization → Prompt appends hardware context
- **SC-011**: Learning goal tone adjustment → Prompt appends goal context
- **SC-012**: Zero data loss → Original content preserved in ref

---

## Implementation Sequence

1. **Phase 0** (30 min): Research & prepare (verify APIs, patterns)
2. **Phase 1** (45 min): Backend foundation (schemas, endpoint, OpenAI service)
3. **Phase 2** (45 min): Frontend component (button, hook, styling)
4. **Phase 3** (30 min): Integration (add to DocItem, wire up logic)
5. **Phase 4** (30 min): Testing & validation (end-to-end tests, edge cases)

**Total**: ~2.5 hours

---

## Next Steps

1. ✅ Specification approved (spec.md passed quality checklist)
2. ✅ Plan documented (this file)
3. ➜ Run `/sp.tasks` to generate implementation tasks
4. ➜ Execute Phase 0-4 sequentially
5. ➜ Test against all success criteria
6. ➜ Create PR to main branch

