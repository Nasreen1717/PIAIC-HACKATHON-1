# Data Model: Urdu Translation Feature

**Date**: 2026-02-01
**Purpose**: Define entities, relationships, and state management for translation feature

---

## Core Entities

### 1. TranslationPreference

**Purpose**: Store user's language preference persistently

```typescript
interface TranslationPreference {
  language: 'en' | 'ur';              // Current selected language
  savedAt: ISO8601DateTime;            // Timestamp of last preference update
  source: 'localStorage' | 'session';  // Where preference is stored
}
```

**Storage**: Browser localStorage under key `translationLanguage`
**Validation**:
- `language` MUST be one of: `'en'` (English) or `'ur'` (Urdu)
- `savedAt` MUST be valid ISO 8601 datetime
- Default if not set: `'en'` (English)

**State Lifecycle**:
```
User loads page
  ↓
[Load preference from localStorage]
  ↓
[Set TranslationPreference.language]
  ↓
[User clicks toggle button]
  ↓
[Update TranslationPreference.language]
  ↓
[Save to localStorage]
  ↓
[Trigger content re-render with new language]
```

**Error Handling**:
- If localStorage unavailable: maintain preference in session-only state; do not persist
- If corrupted preference: fall back to `'en'`

---

### 2. ChapterContent

**Purpose**: Represent chapter structure with translatable and non-translatable sections

```typescript
interface ChapterContent {
  id: string;                                    // Chapter ID (derived from URL/filename)
  title: string;                                 // Chapter title (translatable)
  sections: Section[];                           // Main content sections
  codeBlocks: CodeBlock[];                       // Extracted code blocks
  metadata: {
    module: number;                              // Module 1-4
    chapter: number;                             // Chapter number
    language: 'en' | 'ur';                       // Current language of content
    translatedAt?: ISO8601DateTime;              // When translation was applied
  };
}

interface Section {
  id: string;                                    // Section ID (e.g., "section-1-1")
  heading: string;                               // Section heading (translatable)
  prose: string;                                 // Paragraph text (translatable)
  listItems?: string[];                          // List items (translatable)
  links?: Array<{
    text: string;                                // Link text (translatable)
    href: string;                                // URL (non-translatable)
  }>;
}

interface CodeBlock {
  id: string;                                    // Code block ID
  language: string;                              // Language (e.g., 'python', 'bash')
  code: string;                                  // Code content (non-translatable)
  metadata?: {
    filename?: string;                           // Optional filename label
    highlighted?: boolean;                       // Syntax highlighting applied
  };
}
```

**Extraction Rules**:
1. Extract all `<h1>` through `<h4>` as section headings
2. Extract all `<p>` as prose paragraphs
3. Extract all `<ul>` and `<ol>` as list items
4. Extract all `<a>` as links (preserve href, translate text)
5. Extract all `<pre><code>` and store separately (do NOT translate)

**Validation Rules**:
- `module` MUST be integer in range [1, 4]
- `language` MUST be 'en' or 'ur'
- All prose strings MUST be non-empty after trimming
- All code blocks MUST include language identifier

**Storage**: In-memory during session; derived from DOM at page load

---

### 3. TranslationState

**Purpose**: Track translation operation status and provide real-time UI feedback

```typescript
interface TranslationState {
  isLoading: boolean;                            // Translation API call in progress
  isTranslated: boolean;                         // Content currently in Urdu
  error: TranslationError | null;                // Error (if any)
  cachedTranslation?: string;                    // Optional: cached translated content
  currentLanguage: 'en' | 'ur';                  // Current displayed language
  metadata: {
    startTime?: number;                          // Timestamp of last translation start (ms)
    duration?: number;                           // Translation API latency (ms)
  };
}

interface TranslationError {
  code: string;                                  // Error code (e.g., 'OPENAI_QUOTA_EXCEEDED')
  message: string;                               // User-friendly error message
  severity: 'warning' | 'error';                 // Severity level
  retryable: boolean;                            // Can user retry?
}
```

**Error Codes**:
- `OPENAI_QUOTA_EXCEEDED`: API rate limit or quota exceeded
- `OPENAI_INVALID_KEY`: Invalid or missing API key
- `OPENAI_CONTENT_BLOCKED`: Content blocked by OpenAI safety filters
- `NETWORK_ERROR`: Network timeout or connectivity issue
- `STORAGE_UNAVAILABLE`: localStorage not available; preference not saved
- `PARSE_ERROR`: Failed to parse chapter content

**State Transitions**:
```
[Initial: isLoading=false, isTranslated=false, error=null]
  ↓
[User clicks button] → isLoading=true
  ↓
[API call succeeds] → isLoading=false, isTranslated=true, error=null
  ↓
[User clicks button again] → isTranslated=false
  ↓
(or)
[API call fails] → isLoading=false, error={code, message}, isTranslated=false
  ↓
[User clicks button again to retry] → isLoading=true, error=null
```

**Storage**: React state (in-memory only); no persistence

---

## Relationships

```
┌─────────────────────────────────────────────────────┐
│        User Browser Session                         │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │  TranslationPreference (localStorage)      │   │
│  │  - language: 'en' | 'ur'                   │   │
│  │  - savedAt: timestamp                      │   │
│  └────────────────────────────────────────────┘   │
│           ↓ (determines)                           │
│  ┌────────────────────────────────────────────┐   │
│  │  ChapterContent (in-memory, derived)       │   │
│  │  - id, title, sections[], codeBlocks[]     │   │
│  │  - metadata.language ('en' or 'ur')        │   │
│  └────────────────────────────────────────────┘   │
│           ↓ (rendered)                             │
│  ┌────────────────────────────────────────────┐   │
│  │  TranslationState (React state)            │   │
│  │  - isLoading, isTranslated, error          │   │
│  │  - duration, cachedTranslation             │   │
│  └────────────────────────────────────────────┘   │
│           ↓ (displayed)                            │
│  ┌────────────────────────────────────────────┐   │
│  │  Rendered Chapter HTML (DOM)               │   │
│  │  - English or Urdu prose                   │   │
│  │  - Code blocks unchanged                   │   │
│  │  - Button, loading indicator, error msg    │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## State Management Architecture

### Option 1: React Context (Recommended for MVP)

```typescript
interface TranslationContextType {
  preference: TranslationPreference;
  state: TranslationState;
  translate: (content: ChapterContent) => Promise<string>;
  toggleLanguage: () => Promise<void>;
}

export const TranslationContext = createContext<TranslationContextType | undefined>(undefined);

// Provider component
export function TranslationProvider({ children }) {
  const [preference, setPreference] = useState<TranslationPreference>(() => ({
    language: StorageManager.load('translationLanguage', 'en') as 'en' | 'ur',
    savedAt: new Date().toISOString(),
    source: 'localStorage'
  }));

  const [state, setState] = useState<TranslationState>({
    isLoading: false,
    isTranslated: false,
    error: null,
    currentLanguage: preference.language
  });

  // ... translation logic

  return (
    <TranslationContext.Provider value={{ preference, state, translate, toggleLanguage }}>
      {children}
    </TranslationContext.Provider>
  );
}
```

**Scope**: Wrap `<BrowserRouter>` or `<DocusaurusApp>` to make available to all pages

**Advantages**:
- Simple, React-native, no external dependencies
- State centralized for consistent behavior across chapters
- Easy to test with React Testing Library

### Option 2: Local Component State (Simpler, Isolated)

```typescript
export function TranslationButton() {
  const [preference, setPreference] = useState<TranslationPreference>(() => ({
    language: StorageManager.load('translationLanguage', 'en') as 'en' | 'ur',
    savedAt: new Date().toISOString(),
    source: 'localStorage'
  }));

  const [state, setState] = useState<TranslationState>({
    isLoading: false,
    isTranslated: false,
    error: null,
    currentLanguage: preference.language
  });

  // ... translation logic in component
}
```

**Advantages**:
- Self-contained component
- No context boilerplate
- Perfect for single-button feature

**Disadvantage**:
- State resets on component unmount (acceptable if button always present)

**Decision for MVP**: Use **Option 2** (local state) for rapid prototyping; upgrade to **Option 1** if feature expands to multiple pages/components.

---

## API Contract: OpenAI Translation Endpoint

### Client-Side Call

```typescript
// Frontend: translationApi.ts

async function translateContent(
  content: string,
  targetLanguage: 'ur'
): Promise<{
  translated: string;
  duration: number;
  tokensUsed: { input: number; output: number };
}> {
  const startTime = performance.now();

  const response = await openai.chat.completions.create({
    model: "gpt-4",
    messages: [
      {
        role: "system",
        content: `You are a professional technical translator specializing in robotics and AI education.
Translate the following content from English to Urdu, preserving:
1. All code block syntax (do not translate code blocks)
2. Technical terms in English (e.g., ROS 2, topic, node) - provide Urdu equivalent in parentheses on first occurrence
3. Formatting (headings, lists, emphasis, links)
4. Educational tone (clear, encouraging, accessible)

Output: Return ONLY the translated text in clean Urdu. Do not add explanations or notes.`
      },
      {
        role: "user",
        content: content
      }
    ],
    temperature: 0.3,      // Low temperature for consistency
    max_tokens: 4000,      // Sufficient for chapter content
    top_p: 0.95
  });

  const duration = performance.now() - startTime;
  const translated = response.choices[0].message.content || '';

  return {
    translated,
    duration,
    tokensUsed: {
      input: response.usage?.prompt_tokens || 0,
      output: response.usage?.completion_tokens || 0
    }
  };
}
```

### Request Schema

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "..."
    },
    {
      "role": "user",
      "content": "[chapter content as plain text]"
    }
  ],
  "temperature": 0.3,
  "max_tokens": 4000
}
```

### Response Schema

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "[translated text in Urdu]"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 2500,
    "completion_tokens": 2600
  }
}
```

---

## Validation Rules Summary

| Entity | Field | Rule | Enforcement |
|--------|-------|------|------------|
| TranslationPreference | language | Must be 'en' or 'ur' | Runtime type check |
| TranslationPreference | savedAt | Valid ISO 8601 | Parse, throw on error |
| ChapterContent | id | Non-empty string | Required |
| ChapterContent | module | Integer in [1, 4] | Validation function |
| ChapterContent | language | 'en' or 'ur' | Runtime type check |
| Section | prose | Non-empty after trim | Validation on extraction |
| CodeBlock | language | Non-empty string | Required |
| CodeBlock | code | Non-empty string | Required |
| TranslationState | isLoading | Boolean | Type system |
| TranslationState | currentLanguage | 'en' or 'ur' | Type system |
| TranslationError | code | One of defined codes | Enum |

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interaction                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓ Click "Translate" button
        ┌────────────────────────────────────┐
        │  TranslationButton.tsx              │
        │  - Reads current language           │
        │  - Sets isLoading=true              │
        └────────────┬───────────────────────┘
                     │
                     ↓ Extract chapter content
        ┌────────────────────────────────────┐
        │  contentParser.ts                   │
        │  - Parse DOM                        │
        │  - Return ChapterContent            │
        │  - Separate code blocks             │
        └────────────┬───────────────────────┘
                     │
                     ↓ Call OpenAI API
        ┌────────────────────────────────────┐
        │  translationApi.ts                  │
        │  - Call openai.chat.completions     │
        │  - Track duration                   │
        │  - Return translated text           │
        └────────────┬───────────────────────┘
                     │
                     ↓ Success/Error
        ┌────────────────────────────────────┐
        │  TranslationState                   │
        │  - Set isLoading=false              │
        │  - Set isTranslated=true (or error) │
        │  - Cache translation                │
        └────────────┬───────────────────────┘
                     │
                     ↓ Save preference
        ┌────────────────────────────────────┐
        │  StorageManager.save                │
        │  - Write to localStorage            │
        │  - Update TranslationPreference     │
        └────────────┬───────────────────────┘
                     │
                     ↓ Re-render DOM
        ┌────────────────────────────────────┐
        │  Rendered Chapter (Urdu)            │
        │  - Display translated prose         │
        │  - Code blocks unchanged            │
        │  - Button updated (toggle state)    │
        └────────────────────────────────────┘
```

---

## Database (Optional - Phase 2+)

**Not applicable for MVP**. Phase 2 may add:
- Server-side translation cache (Redis/PostgreSQL)
- Usage analytics (translations per chapter, users, costs)
- QA metrics (translation accuracy, user feedback)

---

## Summary ✅

Data model fully specified with:
- 3 core entities (TranslationPreference, ChapterContent, TranslationState)
- Clear validation rules and error codes
- State management recommendations
- API contracts with request/response schemas
- Data flow diagram

Ready for implementation and API contract testing.
