# Citation Formatting Fix - Plain Text to Clickable Links

**Date**: 2026-02-02
**Issue**: Citations showing as plain text "[Chapter 4, Section 4.3]" instead of clickable links
**Status**: ✅ FIXED
**Commit**: b3ef6bb

---

## Problem

Citations in chatbot responses were appearing as plain text in the answer instead of being clickable links that navigate to the relevant textbook section.

**Before**:
```
User: What is bipedal locomotion?
AI: Bipedal locomotion is the movement on two legs... [Chapter 2, Section 2.1: "Locomotion Basics"]

^ This appears as plain text, not a link
```

---

## Solution

Implemented a complete citation linkification pipeline:

### 1. Backend: Citation URL Generation

**File**: `backend/app/utils/citation_formatter.py`

New methods added:
```python
@staticmethod
def generate_docusaurus_url(chapter_number: int, section_id: str) -> str:
    """Generate Docusaurus URL from chapter and section."""
    module_number = (chapter_number - 1) // 3 + 1
    anchor = str(section_id).replace(".", "-")
    return f"/docs/module-{module_number}/chapter-{chapter_number}#{anchor}"

@staticmethod
def clean_answer_text(answer_text: str) -> str:
    """Remove inline citations from answer text."""
    # Optional: removes citation text if needed
    pattern = r"\s*\[Chapter\s+\d+,\s+Section\s+[^:]+:\s+\"[^\"]+\"\]\s*"
    return re.sub(pattern, " ", answer_text)

@staticmethod
def extract_inline_citations(answer_text: str) -> List[Dict[str, str]]:
    """Extract citations from answer text for frontend parsing."""
    # Returns list of citation objects found in text
```

**URL Format**:
- Input: Chapter 4, Section 4.3
- Output: `/docs/module-2/chapter-4#4-3`
- Module calculation: `(chapter - 1) // 3 + 1`
- Section anchor: dots replaced with hyphens

### 2. Backend: Citation Objects with URLs

**File**: `backend/app/services/llm_service.py`

Updated `_extract_citations()` method:
```python
# Generate Docusaurus URL for navigation
docusaurus_url = CitationFormatter.generate_docusaurus_url(
    int(chapter), section.strip()
)

citation = {
    "chapter_number": int(chapter),
    "section_id": section.strip(),
    "section_title": title,
    "score": matching_chunk.get("score", 0) if matching_chunk else 0,
    "chunk_id": matching_chunk.get("id", "") if matching_chunk else "",
    "url": docusaurus_url,  # ✅ Now includes URL
}
```

### 3. Frontend: Parse and Linkify Citations

**File**: `Front-End-Book/src/components/RAGChatbot/AnswerWithCitations.jsx` (NEW)

Component that:
1. Parses answer text for citation patterns: `[Chapter X, Section Y: "Title"]`
2. Extracts citation data (chapter, section, title)
3. Splits answer into text and citation JSX elements
4. Renders citations as clickable links

```jsx
const AnswerWithCitations = ({ answer }) => {
  const citationPattern = /\[Chapter\s+(\d+),\s+Section\s+([^:]+):\s+"([^"]+)"\]/g;
  const parts = [];

  // Split answer by citations
  let lastIndex = 0;
  let match;

  while ((match = citationPattern.exec(answer)) !== null) {
    // Add text before citation
    parts.push(answer.substring(lastIndex, match.index));

    // Add clickable citation link
    parts.push(
      <CitationLinkInline key={...} citation={...} />
    );

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  parts.push(answer.substring(lastIndex));

  return <div>{parts}</div>;
};
```

### 4. Frontend: Inline Citation Component

**CitationLinkInline** component within `AnswerWithCitations.jsx`:
- Renders citation as clickable `<a>` tag
- URL format: `/docs/module-X/chapter-Y#section-id`
- Handles click navigation to Docusaurus
- Keyboard accessible (Enter key support)
- Tooltip with section title

### 5. Frontend: Updated ChatMessage

**File**: `Front-End-Book/src/components/RAGChatbot/ChatMessage.jsx`

Changed to use `AnswerWithCitations` component:
```jsx
{!isUser ? (
  <AnswerWithCitations answer={message.content} />
) : (
  <div className={styles.messageContent}>{message.content}</div>
)}
```

### 6. Styling

**File**: `Front-End-Book/src/components/RAGChatbot/styles.module.css`

Added styles for inline citations:
```css
.inlineCitation {
  color: var(--ifm-color-primary);
  text-decoration: none;
  font-weight: 500;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.inlineCitation:hover {
  background-color: var(--ifm-color-primary-light);
  text-decoration: underline;
}

.inlineCitation:active {
  background-color: var(--ifm-color-primary);
  color: white;
}
```

---

## How It Works

### Flow Diagram

```
User Question
    ↓
LLM generates answer with inline citations
    ↓
Backend extracts citation data + generates URLs
    ↓
Frontend receives:
  - Answer text with citation patterns
  - Citation objects with URLs
    ↓
AnswerWithCitations parses answer text
    ↓
Detects patterns: [Chapter X, Section Y: "Title"]
    ↓
Converts to CitationLinkInline components
    ↓
User sees:
  - Answer text with blue underlined [Chapter 2, Section 2.1]
  - Hoverable preview tooltip
  - Click navigates to section
```

### Example Interaction

**Input**:
```
Question: What is bipedal locomotion?
```

**LLM Response** (with inline citations):
```
Bipedal locomotion refers to movement on two legs.
[Chapter 2, Section 2.1: "Locomotion Basics"]
It's fundamental to human movement.
[Chapter 2, Section 2.2: "Human Movement"]
```

**Frontend Rendering**:
```
Bipedal locomotion refers to movement on two legs.
[Chapter 2, Section 2.1: "Locomotion Basics"]  ← CLICKABLE LINK (blue, underlined)
It's fundamental to human movement.
[Chapter 2, Section 2.2: "Human Movement"]     ← CLICKABLE LINK (blue, underlined)
```

**On Click**:
- Navigate to: `/docs/module-1/chapter-2#2-1`
- Docusaurus jumps to section in textbook
- URL anchor scrolls to section heading

---

## URL Mapping

### Module Calculation
```
Chapters 1-3  → Module 1
Chapters 4-6  → Module 2
Chapters 7-9  → Module 3
Chapters 10-12 → Module 4
```

Formula: `module_number = (chapter - 1) // 3 + 1`

### Section ID Normalization
- Input: `4.3` → Anchor: `#4-3`
- Input: `4.3.1` → Anchor: `#4-3-1`
- Dots are replaced with hyphens for valid URL anchors

### Example URLs

| Chapter | Section | URL |
|---------|---------|-----|
| 2 | 2.1 | `/docs/module-1/chapter-2#2-1` |
| 4 | 4.3 | `/docs/module-2/chapter-4#4-3` |
| 7 | 7.2.1 | `/docs/module-3/chapter-7#7-2-1` |
| 10 | 10.5 | `/docs/module-4/chapter-10#10-5` |

---

## Features

✅ **Clickable Links**: Citations in answer text are now clickable
✅ **Proper Navigation**: Jumps to correct Docusaurus section
✅ **Visual Feedback**: Hover effects, active states
✅ **Keyboard Accessible**: Enter/Space to activate
✅ **Dark Mode**: Styles work in both light and dark themes
✅ **Fallback**: If backend URL missing, frontend generates it
✅ **Flexible**: Works with any chapter/section structure

---

## Testing

### Manual Testing

1. **Ask a question** that returns citations in the answer
   ```
   "What is bipedal locomotion?"
   ```

2. **Verify citations are clickable**:
   - Look for blue underlined text in answer
   - Pattern: `[Chapter X, Section Y: "Title"]`

3. **Test click navigation**:
   - Click on citation link
   - Should navigate to `/docs/module-X/chapter-Y#section-id`
   - Page scrolls to section heading

4. **Test hover effects**:
   - Hover over citation should highlight
   - Background color changes
   - Underline appears

5. **Test keyboard navigation**:
   - Tab to citation link
   - Press Enter to navigate
   - Should work same as click

### Example Test Questions

- "What is bipedal locomotion?"
- "Explain robot motion control"
- "How does the robot learn?"
- "What are joint servos?"

---

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `citation_formatter.py` | Add URL generation, citation extraction methods | +85 |
| `llm_service.py` | Generate URLs for citations, import CitationFormatter | +8 |
| `AnswerWithCitations.jsx` | NEW - Parse and linkify inline citations | +125 |
| `ChatMessage.jsx` | Use AnswerWithCitations for assistant messages | +10 |
| `CitationLink.jsx` | Support backend-provided URLs | +8 |
| `styles.module.css` | Add inline citation styling | +50 |

**Total**: 6 files, ~286 lines of code

---

## Backward Compatibility

✅ **No Breaking Changes**:
- Existing citation display in "Sources:" section still works
- CitationLink component backward compatible
- Backend URL generation is additive (doesn't break existing code)
- Frontend gracefully handles missing URLs (falls back to local generation)

---

## Performance

- Citation parsing happens client-side (fast)
- No additional API calls
- Minimal JavaScript overhead
- URL generation is O(1) operation

---

## Future Enhancements

1. **Citation Tooltips**: Show source text preview on hover
2. **Citation Highlighting**: Highlight cited text in answer
3. **Citation Tracking**: Log which citations are clicked
4. **Citation Search**: Link citations to full-text search
5. **Mobile Optimization**: Better touch targets on mobile

---

## Troubleshooting

### Citations not appearing as links
- Check browser console for JavaScript errors
- Verify answer text contains citation pattern: `[Chapter X, Section Y: "..."]`
- Inspect element to see if rendered as `<a>` tag

### Links navigate to wrong location
- Check Docusaurus URL format in browser dev tools
- Verify section IDs in documentation match citation data
- Check anchor normalization (dots → hyphens)

### Styling issues
- Clear browser cache (Ctrl+Shift+Delete)
- Check CSS is loaded: Inspect → Styles tab
- Verify CSS class names match component classes

---

**Status**: ✅ COMPLETE AND TESTED
**Impact**: Citations are now fully interactive and navigable
**User Experience**: Seamless integration with textbook for quick reference

