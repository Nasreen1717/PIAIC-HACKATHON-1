# API Contract: Frontend Translation Component

**Purpose**: Define public interface of TranslationButton component

**Framework**: React 19.x, TypeScript

---

## Component: TranslationButton

### Usage

```typescript
import TranslationButton from '@/components/TranslationButton';

export function DocSidebar(props) {
  return (
    <>
      <TranslationButton />
      <DocSidebar {...props} />
    </>
  );
}
```

### Props

```typescript
interface TranslationButtonProps {
  // Optional: override target article element selector
  articleSelector?: string;  // Default: 'article' or '[class*="docMainContainer"]'

  // Optional: callback on translation start/completion
  onTranslationStart?: () => void;
  onTranslationComplete?: (success: boolean) => void;

  // Optional: custom error handler
  onError?: (error: TranslationError) => void;

  // Optional: disable button for specific pages
  disabled?: boolean;
}
```

### Default Props

- `articleSelector`: Docusaurus default article selector (auto-detected)
- `onTranslationStart`: No-op (console log in dev)
- `onTranslationComplete`: No-op
- `onError`: Display error message in UI
- `disabled`: false (button enabled by default)

---

## Hooks & Internal State

### useTranslation()

```typescript
interface UseTranslationReturn {
  // State
  language: 'en' | 'ur';
  isLoading: boolean;
  isTranslated: boolean;
  error: TranslationError | null;

  // Actions
  translate: () => Promise<void>;
  toggleLanguage: () => Promise<void>;
  clearError: () => void;

  // Metadata
  lastTranslationDuration?: number;
}

const useTranslation = (): UseTranslationReturn => {
  // Implementation
};

// Usage in TranslationButton
const { language, isLoading, error, toggleLanguage } = useTranslation();
```

---

## Helper Functions

### Content Parser

```typescript
interface ParsedContent {
  translatable: string;      // HTML/plaintext with code blocks removed
  codeBlocks: CodeBlock[];   // Extracted code blocks
}

export function parseChapterContent(
  articleElement: HTMLElement
): ParsedContent
```

**Algorithm**:
1. Clone article DOM
2. Extract all `<pre><code>` blocks, replace with placeholder
3. Extract remaining `innerText`
4. Return translatable text + code blocks array

**Error Handling**:
- If `articleElement` is null: throw error
- If no content found: return empty string with warning

### Storage Manager

```typescript
export const StorageManager = {
  save: (key: string, value: string): boolean => {
    // Try localStorage; catch errors
    // Return true if successful, false otherwise
  },

  load: (key: string, fallback: string): string => {
    // Try localStorage; catch errors
    // Return loaded value or fallback
  },

  clear: (key: string): boolean => {
    // Try to clear; return success
  }
};
```

---

## UI Events & State

### Button Click Handler

```typescript
async function handleTranslate() {
  // 1. Check if already translated
  if (isTranslated) {
    // 2a. Toggle back to English: update DOM, save preference
    revertToEnglish();
    toggleLanguage();
  } else {
    // 2b. Translate to Urdu
    try {
      setIsLoading(true);
      setError(null);

      // Extract content
      const article = document.querySelector(articleSelector);
      if (!article) throw new Error('Article not found');

      const { translatable, codeBlocks } = parseChapterContent(article);

      // Call OpenAI API
      const result = await translateContent(translatable);

      // Update DOM with translated text
      reinsertTranslatedContent(article, result.translated, codeBlocks);

      // Update state
      setIsTranslated(true);
      setLanguage('ur');
      StorageManager.save('translationLanguage', 'ur');

      onTranslationComplete?.(true);

    } catch (err) {
      setError(err);
      setIsTranslated(false);
      onTranslationComplete?.(false);
    } finally {
      setIsLoading(false);
    }
  }
}
```

### UI Feedback

```typescript
// Loading state
{isLoading && <LoadingSpinner />}

// Error state
{error && (
  <ErrorMessage
    code={error.code}
    message={error.message}
    onRetry={() => handleTranslate()}
    onDismiss={() => setError(null)}
  />
)}

// Success: button label changes
{isTranslated ? 'Back to English 🌐' : 'Translate to Urdu 🌐'}
```

---

## Accessibility Requirements

### WCAG 2.1 AA Compliance

- Button has `aria-label="Translate to Urdu"` or `aria-label="Back to English"`
- Button `aria-disabled` reflects loading state
- Loading indicator has `role="status"` and `aria-live="polite"`
- Error messages have `role="alert"` and `aria-live="assertive"`
- Keyboard navigation: Tab to button, Enter/Space to activate
- No color-only indicator (use text + icon)

### Testing

```typescript
describe('TranslationButton a11y', () => {
  it('should have proper ARIA labels', () => {
    const button = render(<TranslationButton />);
    expect(button).toHaveAttribute('aria-label');
  });

  it('should be keyboard navigable', () => {
    const button = screen.getByRole('button');
    button.focus();
    userEvent.keyboard('{Enter}');
    expect(onTranslate).toHaveBeenCalled();
  });

  it('loading state should be announced', () => {
    render(<TranslationButton />);
    userEvent.click(screen.getByRole('button'));
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
});
```

---

## Composition & Style

### Component Structure

```typescript
export default function TranslationButton(props: TranslationButtonProps) {
  return (
    <div className={styles.translationButtonContainer}>
      <button
        className={styles.button}
        onClick={handleTranslate}
        disabled={isLoading || props.disabled}
        aria-label={ariaLabel}
        aria-disabled={isLoading}
      >
        {isLoading ? (
          <>
            <span className={styles.spinner} />
            <span>Translating...</span>
          </>
        ) : (
          <>
            <span className={styles.icon}>🌐</span>
            <span>{buttonLabel}</span>
          </>
        )}
      </button>

      {error && (
        <ErrorAlert
          error={error}
          onRetry={handleTranslate}
          onDismiss={() => setError(null)}
        />
      )}
    </div>
  );
}
```

### Styling (TranslationButton.module.css)

```css
.translationButtonContainer {
  margin-bottom: 1rem;
  padding: 0.5rem 0;
}

.button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 200ms ease;
}

.button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.icon {
  font-size: 1.1rem;
}

.spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

---

## Error Boundaries

```typescript
interface ErrorAlert {
  error: TranslationError;
  onRetry: () => void;
  onDismiss: () => void;
}

function ErrorAlert({ error, onRetry, onDismiss }: ErrorAlert) {
  const errorMessages = {
    OPENAI_QUOTA_EXCEEDED: 'Too many requests. Please try again in a moment.',
    OPENAI_API_KEY_INVALID: 'Configuration error. Contact support.',
    NETWORK_ERROR: 'Network issue. Check your connection and try again.',
    PARSE_ERROR: 'Failed to process content. Try a smaller section.',
    STORAGE_UNAVAILABLE: 'Preference not saved (private browsing?).',
  };

  return (
    <div className={styles.errorAlert} role="alert" aria-live="assertive">
      <p className={styles.errorMessage}>
        {errorMessages[error.code] || error.message}
      </p>
      {error.retryable && (
        <button onClick={onRetry} className={styles.retryButton}>
          Try Again
        </button>
      )}
      <button onClick={onDismiss} className={styles.dismissButton}>
        ✕ Dismiss
      </button>
    </div>
  );
}
```

---

## Event Flow

```
User clicks "Translate to Urdu 🌐"
  ↓
isLoading → true, button disabled, spinner shown
  ↓
Extract article element → parse content
  ↓
Call openai.chat.completions.create()
  ↓
Success:
  ├─ Display translated content
  ├─ Update button to "Back to English 🌐"
  ├─ Save preference (localStorage)
  └─ Call onTranslationComplete(true)

Failure:
  ├─ Show error message with retry button
  ├─ Revert to English
  ├─ Do NOT save preference
  └─ Call onTranslationComplete(false)

Finally:
  └─ isLoading → false, button re-enabled
```

---

## Testing Requirements

### Unit Tests (Jest + React Testing Library)

- ✅ Component renders button with correct label
- ✅ Button click triggers translation
- ✅ Loading state displays spinner
- ✅ Error message shows on API failure
- ✅ Preference saved on successful translation
- ✅ Toggle works (translate → revert)
- ✅ Keyboard navigation works

### Integration Tests

- ✅ Button integrates into Docusaurus theme
- ✅ Translation persists across page reloads
- ✅ Works in Modules 1-4 chapters only

### Manual Tests

- ✅ Visual inspection: button placement, styling
- ✅ Accessibility: screen reader, keyboard nav
- ✅ Error handling: network off, API key invalid
- ✅ Performance: <3 second translation time

---

## Dependencies

```json
{
  "dependencies": {
    "react": "^19.0.0",
    "openai": "^4.0.0"
  },
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "jest": "^29.0.0"
  }
}
```

---

## Future Enhancements (Phase 2+)

- [ ] Backend proxy for API key security
- [ ] Translation caching (Redis)
- [ ] Multiple target languages (Chinese, Spanish, etc.)
- [ ] UI localization to Urdu
- [ ] Inline editing + feedback mechanism
- [ ] Analytics & quality metrics
