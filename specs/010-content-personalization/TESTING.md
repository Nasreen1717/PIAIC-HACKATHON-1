# Testing Guide: Content Personalization Feature

This guide provides step-by-step instructions to test all user stories for the content personalization feature.

## Prerequisites

1. Backend running: `cd backend && python -m uvicorn app.main:app --reload`
2. Frontend running: `cd Front-End-Book && npm run start`
3. Sample user accounts created during signup with different skill levels

---

## Phase 3: User Story 1 - Beginner Gets Simplified Content (P1)

### Test Setup
1. Sign in as a beginner user (or create one):
   - Email: beginner@test.local
   - Software Background: **beginner**
   - Hardware Background: **none**
   - Learning Goal: **career**

### Manual Test: E2E Beginner Personalization

**Step 1: Navigate to Chapter**
- Open any chapter in the textbook (e.g., "Intro to Robotics")
- Observe the "Personalize for Me" button appears at the start of the article

**Step 2: Click Personalize Button**
- Click "Personalize for Me" button
- Observe loading spinner with "Personalizing..." message
- Wait for API response (should take < 8 seconds)

**Step 3: Verify Content Transformation**
- Content should be noticeably simpler
- Look for:
  - ✅ Simple, everyday language (no jargon)
  - ✅ Step-by-step explanations with numbered lists
  - ✅ 💡 Tip boxes (highlighted key concepts)
  - ✅ ⚠️ Common Mistake sections
  - ✅ Glossary links for technical terms
  - ✅ Real-world analogies to familiar concepts
  - ✅ Detailed code comments explaining logic

**Step 4: Verify Content Preservation**
- Check for IEEE citations:
  - ✅ All citations remain in original format [N]
  - ✅ No citations added or removed
- Check for code examples:
  - ✅ All code blocks remain exactly unchanged
  - ✅ No code modifications, no added/removed lines
- Check for facts:
  - ✅ All technical facts remain accurate
  - ✅ No version numbers changed
  - ✅ No API names changed

**Step 5: Verify Reading Level**
- Use automated readability scorer (e.g., https://readability-score.com/)
- Paste personalized content
- Verify Flesch-Kincaid Grade Level is 12-14

**Step 6: Verify Reset**
- Click "Reset to Original" button
- Content should instantly return to original (< 50ms)
- Button should change back to "Personalize for Me"

**Step 7: Verify Mobile (Optional)**
- Open on mobile device (iOS Safari or Android Chrome)
- Button should be visible and clickable (48px+ height)
- Content should be readable on small screen
- Reset should work on mobile

### Backend Validation (curl)

```bash
# Get JWT token first (sign in as beginner user)
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "beginner@test.local", "password": "your-password"}' \
  | jq '.access_token'

# Save token in variable
TOKEN="your-jwt-token-here"

# Test beginner personalization
curl -X POST http://localhost:8000/api/v1/personalize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Chapter: Advanced Kinematics\n\nThis chapter covers the Denavit-Hartenberg convention [1] for representing robot kinematics. The DH convention uses four parameters...",
    "hardware_background": "none",
    "learning_goal": "career"
  }' | jq '.'
```

**Expected Response:**
```json
{
  "personalized_content": "# Chapter: Advanced Kinematics\n\nLet's learn about how robots understand their position and movement...",
  "personalization_level": "beginner",
  "metadata": {
    "processing_time_ms": 2500,
    "tokens_used": 450,
    "model": "gpt-4",
    "personalization_level": "beginner"
  }
}
```

### Acceptance Criteria
- [x] Button visible to beginner users
- [x] Loading spinner shows for 2-8 seconds
- [x] Content is simplified with tips/mistakes/glossary
- [x] 100% of citations preserved
- [x] 100% of code examples preserved
- [x] Reading level is Flesch-Kincaid 12-14
- [x] Reset button works instantly
- [x] Mobile responsive (48px+ button)

---

## Phase 4: User Story 2 - Advanced Gets Research-Focused Content (P1)

### Test Setup
1. Sign in as an advanced user (or create one):
   - Email: advanced@test.local
   - Software Background: **advanced**
   - Hardware Background: **advanced**
   - Learning Goal: **research**

### Manual Test: E2E Advanced Personalization

**Step 1: Navigate to Chapter**
- Open same chapter as US1
- Click "Personalize for Me" button

**Step 2: Verify Content Transformation**
- Content should be concise and technical
- Look for:
  - ✅ Professional technical terminology
  - ✅ Assumes CS/robotics background (no explanations)
  - ✅ Information-dense paragraphs
  - ✅ Performance optimization tips and benchmarks
  - ✅ Seminal papers highlighted in citations
  - ✅ Advanced use cases and novel approaches
  - ✅ Minimal code comments focused on complex patterns
  - ✅ Hardware deployment emphasis (RTX, Jetson, CUDA optimization)

**Step 3: Verify Content Preservation**
- ✅ All citations remain unchanged
- ✅ All code examples unchanged
- ✅ All technical facts accurate

**Step 4: Verify Citations Are Research-Relevant**
- Citations should be highlighted or emphasized as seminal papers
- References should include research-focused context

**Step 5: Verify Hardware Context**
- Content should emphasize:
  - RTX/Jetson GPU deployment
  - CUDA optimization strategies
  - Hardware performance benchmarks
  - Sim-to-real transfer techniques

**Step 6: Reset and Verify**
- Click "Reset to Original"
- Content should return to original
- Compare with US1 - should be different (advanced vs beginner)

### Backend Validation (curl)

```bash
# Test advanced personalization
curl -X POST http://localhost:8000/api/v1/personalize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Chapter: Advanced Kinematics\n\nThis chapter covers the Denavit-Hartenberg convention [1]...",
    "hardware_background": "advanced",
    "learning_goal": "research"
  }' | jq '.personalization_level'
```

**Expected:** `"advanced"`

### Acceptance Criteria
- [x] Content is concise and technical
- [x] Assumes CS/robotics background
- [x] Performance optimization tips included
- [x] Seminal papers highlighted
- [x] Advanced use cases present
- [x] 100% of citations preserved
- [x] 100% of code examples preserved
- [x] Hardware deployment emphasis (RTX/Jetson)
- [x] Reset works correctly

---

## Phase 5: User Story 3 - Intermediate Gets Balanced Content (P2)

### Test Setup
1. Sign in as an intermediate user (or create one):
   - Email: intermediate@test.local
   - Software Background: **intermediate**
   - Hardware Background: **basic**
   - Learning Goal: **career**

### Manual Test: E2E Intermediate Personalization

**Step 1: Navigate to Chapter**
- Open same chapter as US1 and US2
- Click "Personalize for Me" button

**Step 2: Verify Content Transformation**
- Content should use balanced technical language
- Look for:
  - ✅ Technical with brief explanations
  - ✅ Standard paragraph flow (not oversimplified, not overly dense)
  - ✅ Best practice callouts
  - ✅ Moderate code comments
  - ✅ Balance between simulation and hardware options
  - ✅ Simulation-first emphasis (Gazebo, Isaac Sim)
  - ✅ CPU alternatives mentioned
  - ✅ GPU upgrade path shown but not required

**Step 3: Verify Hardware Context**
- Should emphasize:
  - Simulation tools (Gazebo, Isaac Sim)
  - CPU-based alternatives
  - GPU upgrade path (mentioned but optional)

**Step 4: Compare Across Skill Levels**
- Open US1 (beginner) and US3 (intermediate) side-by-side
- Intermediate should have:
  - Fewer explanations than beginner
  - More technical depth than beginner
  - But less depth than advanced

**Step 5: Verify Content Preservation**
- ✅ All citations preserved
- ✅ All code examples preserved
- ✅ All technical facts accurate

### Backend Validation (curl)

```bash
# Test intermediate personalization
curl -X POST http://localhost:8000/api/v1/personalize \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "# Chapter: Advanced Kinematics\n\nThis chapter covers the Denavit-Hartenberg convention [1]...",
    "hardware_background": "basic",
    "learning_goal": "career"
  }' | jq '.personalization_level'
```

**Expected:** `"intermediate"`

### Acceptance Criteria
- [x] Balanced technical language (not oversimplified, not overly dense)
- [x] Best practices included
- [x] Moderate code comments
- [x] Simulation tools (Gazebo/Isaac Sim) emphasized
- [x] CPU alternatives provided
- [x] GPU upgrade path mentioned but not required
- [x] 100% of citations preserved
- [x] 100% of code examples preserved

---

## Phase 6: User Story 4 - Hardware Context Switching (P2)

### Test Setup
1. Create intermediate user with hardware progression:
   - Email: hardware-test@test.local
   - Software Background: intermediate
   - Initial Hardware Background: **none**
   - Learning Goal: career

### Manual Test: Hardware Context Switching

**Step 1: First Personalization (No Hardware)**
- Sign in with initial profile (hardware: none)
- Personalize chapter
- Observe cloud emphasis:
  - ✅ NVIDIA Isaac Cloud mentioned
  - ✅ AWS RoboMaker mentioned
  - ✅ GCP options mentioned
  - ✅ Docker containers and cloud setup

**Step 2: Update Hardware Profile**
- Go to profile settings
- Update Hardware Background: **advanced**
- Verify profile saved

**Step 3: Re-personalize Same Chapter**
- Navigate back to chapter
- Click "Personalize for Me" again
- Observe hardware deployment emphasis:
  - ✅ Hardware deployment emphasized
  - ✅ Sim-to-real transfer mentioned
  - ✅ CUDA optimization shown
  - ✅ Jetson Orin deployment highlighted
  - ✅ Performance benchmarks for hardware

**Step 4: Verify Context Switch Works**
- Compare first personalization (cloud) vs second (hardware)
- Content should be noticeably different in hardware emphasis
- Technical facts should remain unchanged

**Step 5: Reset and Verify**
- Click "Reset to Original" after second personalization
- Original content should be restored
- First personalization state should NOT interfere

### Acceptance Criteria
- [x] First personalization uses cloud emphasis (hardware: none)
- [x] Second personalization uses hardware emphasis (hardware: advanced)
- [x] Profile update properly reflected in new personalization
- [x] Reset always returns to original
- [x] Previous personalization state doesn't interfere

---

## Phase 7: User Story 5 - Learning Goals Influence Tone (P3)

### Test Setup
1. Create three users with different learning goals (all intermediate skill):
   - Email: goal-career@test.local, Software: intermediate, Learning Goal: **career**
   - Email: goal-hobby@test.local, Software: intermediate, Learning Goal: **hobby**
   - Email: goal-research@test.local, Software: intermediate, Learning Goal: **research**

### Manual Test: Learning Goal Tone

**Test 1: Career Goal**
- Sign in as goal-career user
- Personalize chapter
- Look for:
  - ✅ Professional tone
  - ✅ Job market relevance
  - ✅ Industry applications
  - ✅ Career advancement focus

**Test 2: Hobby Goal**
- Sign in as goal-hobby user
- Personalize same chapter
- Look for:
  - ✅ Enthusiastic tone
  - ✅ Fun and creative exploration
  - ✅ DIY and personal project examples
  - ✅ Creative applications

**Test 3: Research Goal**
- Sign in as goal-research user
- Personalize same chapter
- Look for:
  - ✅ Academic tone
  - ✅ Novel approaches and research papers
  - ✅ State-of-the-art techniques
  - ✅ Research applications and implications

**Step 4: Compare Tone Differences**
- Open all three personalized versions side-by-side
- Verify tone is noticeably different:
  - Career: Professional
  - Hobby: Enthusiastic
  - Research: Academic
- Verify technical facts remain identical across all three

### Acceptance Criteria
- [x] Career goal shows professional tone and industry relevance
- [x] Hobby goal shows enthusiastic tone and fun examples
- [x] Research goal shows academic tone and novel approaches
- [x] Technical facts identical across all three
- [x] Code examples identical across all three
- [x] Citations identical across all three

---

## Phase 8: Error Handling & Edge Cases

### Error Test 1: OpenAI Timeout (>10s)
1. Mock or simulate slow OpenAI response
2. Should see "Service took too long to respond" error
3. Original content should remain intact
4. Retry button should work

### Error Test 2: Invalid JWT
1. Try to call endpoint without Authorization header
2. Should get 401 Unauthorized
3. Frontend should show "Your session expired" and redirect to signin

### Error Test 3: Rate Limit (429)
1. Rapid-fire personalization requests (5+ within 1 minute)
2. Should eventually hit rate limit
3. Should show "Service is busy. Please wait a moment and try again"
4. Retry after wait should succeed

### Error Test 4: Network Error
1. Disconnect network during personalization
2. Should show "Network error. Please check your connection and try again"
3. Retry after reconnecting should work

### Error Test 5: Empty Content
1. Navigate to page without article element (if possible)
2. Click button - should show "No article content found"

### Error Test 6: Rapid Clicks (Debounce)
1. Click "Personalize for Me" 10 times rapidly
2. Should only send 1 API request (not 10)
3. Should not show 10 spinners

---

## Phase 9: Performance & Mobile

### Performance Test 1: Response Time
1. Use browser DevTools Network tab
2. Personalize content
3. Total time from click to content displayed: **< 8 seconds**
4. Track:
   - API call time (typically 2-4 seconds)
   - Frontend rendering (should be < 200ms)

### Performance Test 2: State Transitions
1. Observe button state changes:
   - Click → Loading spinner appears immediately (< 100ms)
   - Response → "Personalized" state appears (< 200ms)
   - Click Reset → Original state appears instantly (< 50ms)

### Performance Test 3: No UI Jank
1. Personalize content while scrolling
2. Should not freeze or jank
3. Scrolling should remain smooth

### Mobile Test 1: iOS Safari
1. Open on iPhone/iPad in Safari
2. Button visible and clickable (48px+ height)
3. Content readable on small screen (no horizontal scroll)
4. All states visible on mobile
5. Touch works correctly (no double-tap required)

### Mobile Test 2: Android Chrome
1. Open on Android phone in Chrome
2. Same verification as iOS

---

## Citation Preservation Validation

**Automated Check (Python):**
```python
import re

def extract_citations(text):
    """Extract IEEE-style citations [N] from text."""
    return re.findall(r'\[\d+\]', text)

# Compare original and personalized
original_citations = extract_citations(original_content)
personalized_citations = extract_citations(personalized_content)

# Should be identical
assert set(original_citations) == set(personalized_citations), \
    "Citations not preserved!"
```

**Manual Check:**
1. Find all citations in original content: `[1]`, `[2]`, etc.
2. Verify each citation appears in personalized content
3. Verify citation numbers are unchanged
4. Verify citation format is unchanged

---

## Code Preservation Validation

**Manual Check:**
1. Find all code blocks in original (between ``` markers)
2. For each code block:
   - Copy code from original
   - Copy code from personalized
   - Compare byte-for-byte (should be identical)
   - Check no lines added or removed
   - Check indentation unchanged

---

## Success Checklist

### User Story Completeness
- [x] US1 (Beginner): Simplified content with tips/mistakes
- [x] US2 (Advanced): Research-focused with optimization
- [x] US3 (Intermediate): Balanced technical
- [x] US4 (Hardware Switching): Dynamic personalization
- [x] US5 (Learning Goals): Tone adjustment

### Quality Guarantees
- [x] 100% citation preservation across all stories
- [x] 100% code preservation across all stories
- [x] All technical facts unchanged across all stories
- [x] Reading levels appropriate (beginner 12-14, others balanced)
- [x] Hardware context properly applied
- [x] Learning goals properly applied

### Error Handling
- [x] Timeout handling (8s+)
- [x] Rate limiting (429)
- [x] Auth failure (401)
- [x] Network errors
- [x] Invalid content (400)
- [x] Server errors (500)

### Performance
- [x] Personalization < 8 seconds
- [x] State transitions < 200ms
- [x] Reset < 50ms
- [x] Mobile responsive
- [x] No UI jank

### Mobile
- [x] Button visible on mobile (48px+)
- [x] Content readable on small screens
- [x] Touch interactions work
- [x] All states visible on mobile

---

## Test Summary Template

```markdown
## US1 Beginner - ✅ PASS
- Button visible: ✅
- Content simplified: ✅
- Citations preserved: ✅
- Code preserved: ✅
- Reading level 12-14: ✅
- Reset works: ✅

## US2 Advanced - ✅ PASS
- Content technical: ✅
- Research focused: ✅
- Citations preserved: ✅
- Code preserved: ✅
- Hardware deployment emphasis: ✅

## US3 Intermediate - ✅ PASS
- Balanced technical: ✅
- Best practices: ✅
- Simulation emphasis: ✅
- Citations preserved: ✅
- Code preserved: ✅

## US4 Hardware Switching - ✅ PASS
- Cloud (hardware: none): ✅
- Hardware (hardware: advanced): ✅
- Profile update reflected: ✅
- Reset works: ✅

## US5 Learning Goals - ✅ PASS
- Career (professional): ✅
- Hobby (enthusiastic): ✅
- Research (academic): ✅
- Tech facts identical: ✅

## Error Handling - ✅ PASS
- Timeout: ✅
- Rate limit: ✅
- Auth error: ✅
- Network error: ✅
- Debounce works: ✅

## Performance - ✅ PASS
- Personalization < 8s: ✅
- State transitions < 200ms: ✅
- Reset < 50ms: ✅
- Mobile responsive: ✅
- No jank: ✅

## Overall: ✅ PRODUCTION READY
```
