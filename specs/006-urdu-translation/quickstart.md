# Quickstart: Urdu Translation Feature Development

**Objective**: Set up development environment and test translation feature end-to-end

**Time**: ~15 minutes (first run only; subsequent runs are instant)

---

## Prerequisites

- Node.js 20+ and npm 9+ installed
- OpenAI API key (get from [platform.openai.com](https://platform.openai.com))
- Terminal/command line access
- Code editor (VS Code recommended)

---

## Step 1: Set Up Environment

### 1.1 Clone/Navigate to Repository

```bash
cd /mnt/d/code/Hackathon-1/Front-End-Book
```

### 1.2 Install Dependencies

```bash
npm install
```

This installs:
- `@docusaurus/core` (3.9.2)
- `@docusaurus/preset-classic` (3.9.2)
- `react` (19.x)
- `openai` (latest ^4.x - add if not already present)

**Add OpenAI SDK if missing**:

```bash
npm install openai
```

### 1.3 Create Environment File

Create `.env.local` in `Front-End-Book/` directory:

```bash
# Get your API key from https://platform.openai.com/account/api-keys
REACT_APP_OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

**Security Note**: Never commit `.env.local` to version control. Add to `.gitignore`:

```bash
echo ".env.local" >> .gitignore
```

---

## Step 2: Create Translation Component

### 2.1 Create Component Directory

```bash
mkdir -p src/components/TranslationButton/__tests__
```

### 2.2 Create TranslationButton.tsx

**File**: `Front-End-Book/src/components/TranslationButton/TranslationButton.tsx`

```typescript
import React, { useState, useCallback } from 'react';
import { OpenAI } from 'openai';
import styles from './TranslationButton.module.css';

interface TranslationError {
  code: string;
  message: string;
  retryable: boolean;
}

export default function TranslationButton() {
  const [isLoading, setIsLoading] = useState(false);
  const [isTranslated, setIsTranslated] = useState(false);
  const [error, setError] = useState<TranslationError | null>(null);

  const openai = new OpenAI({
    apiKey: process.env.REACT_APP_OPENAI_API_KEY,
    dangerouslyAllowBrowser: true,
  });

  const parseChapterContent = useCallback((articleElement: HTMLElement) => {
    const clone = articleElement.cloneNode(true) as HTMLElement;
    const codeBlocks: Array<{ language: string; code: string }> = [];

    // Extract code blocks
    clone.querySelectorAll('pre code').forEach((block, index) => {
      const language =
        block.className.match(/language-(\w+)/)?.[1] || 'plaintext';
      codeBlocks.push({
        language,
        code: block.textContent || '',
      });
      const pre = block.closest('pre');
      if (pre) {
        pre.textContent = `[CODE_BLOCK_${index}]`;
      }
    });

    return {
      translatable: clone.innerText,
      codeBlocks,
    };
  }, []);

  const translateContent = useCallback(
    async (content: string) => {
      try {
        const response = await openai.chat.completions.create({
          model: 'gpt-4',
          messages: [
            {
              role: 'system',
              content: `You are a professional technical translator specializing in robotics and AI education.
Translate the following content from English to Urdu, preserving all formatting, code blocks, and links.
Return ONLY the translated text in clean Urdu.`,
            },
            {
              role: 'user',
              content: content,
            },
          ],
          temperature: 0.3,
          max_tokens: 4000,
        });

        return (
          response.choices[0]?.message?.content || ''
        );
      } catch (err: any) {
        if (err.status === 429) {
          throw {
            code: 'OPENAI_QUOTA_EXCEEDED',
            message: 'Rate limit exceeded. Please try again in a moment.',
            retryable: true,
          };
        }
        throw {
          code: 'TRANSLATION_FAILED',
          message: err.message || 'Translation failed. Please try again.',
          retryable: true,
        };
      }
    },
    [openai]
  );

  const handleTranslate = useCallback(async () => {
    if (isTranslated) {
      // Revert to English
      setIsTranslated(false);
      setError(null);
      // Reload page to restore original content
      window.location.reload();
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const article = document.querySelector('article');
      if (!article) {
        throw {
          code: 'ARTICLE_NOT_FOUND',
          message: 'Could not find chapter content.',
          retryable: false,
        };
      }

      const { translatable, codeBlocks } =
        parseChapterContent(article);

      const translated = await translateContent(translatable);

      // Update DOM with translated content
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = translated;
      article.innerHTML = tempDiv.innerHTML;

      // Restore code blocks (simplified - reinsert as text)
      let replacedText = article.innerHTML;
      codeBlocks.forEach((block, index) => {
        replacedText = replacedText.replace(
          `[CODE_BLOCK_${index}]`,
          `<pre><code class="language-${block.language}">${escapeHtml(block.code)}</code></pre>`
        );
      });
      article.innerHTML = replacedText;

      setIsTranslated(true);
      // Save preference
      try {
        localStorage.setItem('translationLanguage', 'ur');
      } catch (e) {
        console.warn('localStorage unavailable:', e);
      }
    } catch (err: any) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, [isTranslated, parseChapterContent, translateContent]);

  function escapeHtml(text: string): string {
    const map: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;',
    };
    return text.replace(/[&<>"']/g, (char) => map[char]);
  }

  return (
    <div className={styles.container}>
      <button
        className={styles.button}
        onClick={handleTranslate}
        disabled={isLoading}
        aria-label={
          isTranslated ? 'Translate back to English' : 'Translate to Urdu'
        }
      >
        {isLoading ? (
          <>
            <span className={styles.spinner} />
            <span>Translating...</span>
          </>
        ) : (
          <>
            <span className={styles.icon}>🌐</span>
            <span>{isTranslated ? 'Back to English' : 'Translate to Urdu'}</span>
          </>
        )}
      </button>

      {error && (
        <div className={styles.error} role="alert">
          <p>{error.message}</p>
          {error.retryable && (
            <button onClick={handleTranslate} className={styles.retryButton}>
              Try Again
            </button>
          )}
        </div>
      )}
    </div>
  );
}
```

### 2.3 Create CSS Module

**File**: `Front-End-Book/src/components/TranslationButton/TranslationButton.module.css`

```css
.container {
  margin-bottom: 1.5rem;
  padding: 0.5rem 0;
}

.button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.25rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  transition: all 200ms ease;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.5);
}

.button:active:not(:disabled) {
  transform: translateY(0);
}

.button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.icon {
  font-size: 1.1rem;
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error {
  margin-top: 0.75rem;
  padding: 0.75rem 1rem;
  background-color: #fee;
  border-left: 4px solid #c33;
  border-radius: 4px;
  color: #c33;
  font-size: 0.9rem;
}

.error p {
  margin: 0 0 0.5rem 0;
}

.retryButton {
  padding: 0.4rem 0.8rem;
  background-color: #c33;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
}

.retryButton:hover {
  background-color: #a22;
}
```

### 2.4 Create Index Export

**File**: `Front-End-Book/src/components/TranslationButton/index.ts`

```typescript
export { default } from './TranslationButton';
```

---

## Step 3: Integrate into Docusaurus Theme

### 3.1 Swizzle DocSidebar Component

```bash
npm run swizzle @docusaurus/preset-classic DocSidebar -- --typescript
```

This creates a wrappable copy at `src/theme/DocSidebar.tsx`

### 3.2 Modify Swizzled Component

**File**: `src/theme/DocSidebar.tsx` (or `src/theme/DocSidebar.jsx`)

Add TranslationButton import and render at top of article:

```typescript
// At top of file:
import TranslationButton from '@/components/TranslationButton';

// In render (example - modify based on actual structure):
export default function DocSidebarWrapper(props) {
  return (
    <>
      <div className="doc-content-wrapper">
        <TranslationButton />
        <DocSidebar {...props} />
      </div>
    </>
  );
}
```

---

## Step 4: Test the Feature

### 4.1 Start Development Server

```bash
npm start
```

This starts Docusaurus at `http://localhost:3000`

### 4.2 Manual Testing

1. Navigate to any chapter in Modules 1-4 (e.g., "Chapter 1: ROS 2 Architecture")
2. Look for "Translate to Urdu 🌐" button at top of content
3. Click the button
4. Observe:
   - Button shows "Translating..." with spinner
   - After 2-3 seconds: content changes to Urdu
   - Button label changes to "Back to English 🌐"
5. Click "Back to English" → content reverts
6. Refresh page → preference should be restored if localStorage works

### 4.3 Verify Code Block Preservation

- Check that code examples remain in original language/format
- Verify syntax highlighting still works
- Confirm no translation of code

### 4.4 Test Error Handling

- Unset `REACT_APP_OPENAI_API_KEY` in `.env.local`
- Reload page, click button
- Verify error message displays: "Configuration error"
- Set API key again, click "Try Again" → should work

---

## Step 5: Run Tests (Optional)

### 5.1 Create Simple Test

**File**: `src/components/TranslationButton/__tests__/TranslationButton.test.tsx`

```typescript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import TranslationButton from '../TranslationButton';

describe('TranslationButton', () => {
  it('renders button with correct label', () => {
    render(<TranslationButton />);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('Translate to Urdu');
  });

  it('shows loading state on click', () => {
    render(<TranslationButton />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    // Button should be disabled during loading
    expect(button).toBeDisabled();
  });
});
```

### 5.2 Run Tests

```bash
npm test -- TranslationButton
```

---

## Step 6: Build for Production

### 6.1 Build Static Site

```bash
npm run build
```

This generates optimized output in `build/` directory

### 6.2 Verify Built Site

```bash
npm run serve
```

Visit `http://localhost:3000` and verify translation feature works in built version

---

## Troubleshooting

### Issue: "API key not found" error

**Solution**:
- Verify `.env.local` exists in `Front-End-Book/` directory
- Check environment variable name: must be `REACT_APP_OPENAI_API_KEY` (Docusaurus/CRA convention)
- Restart dev server after adding `.env.local`

### Issue: Button doesn't appear

**Solution**:
- Verify DocSidebar swizzle completed: check `src/theme/DocSidebar.tsx` exists
- Verify TranslationButton import is correct path
- Check browser console (F12) for import errors
- Restart dev server

### Issue: Translation takes >10 seconds or times out

**Solution**:
- Check network connection (slow upload speed?)
- Verify OpenAI API status: https://status.openai.com/
- Check if OpenAI rate limit reached (check account page)
- Try with smaller chapter (chapter 1 usually smallest)

### Issue: Urdu text displays as boxes/gibberish

**Solution**:
- Ensure browser supports Unicode 15.0 (all modern browsers do)
- Clear browser cache: Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
- Try different browser (Chrome, Firefox) to isolate issue

### Issue: "localStorage unavailable" warning

**Solution**:
- Feature still works (translation occurs, preference just not saved)
- This warning is expected in private/incognito browsing
- On regular tabs, this indicates a configuration issue - contact support

---

## Next Steps

1. ✅ Develop and test in local environment
2. ➡️ Run full test suite (unit + integration)
3. ➡️ Get QA review on Urdu translation quality (95% accuracy baseline)
4. ➡️ Deploy to staging environment
5. ➡️ Collect user feedback
6. ➡️ Deploy to production

---

## Additional Resources

- [Docusaurus Swizzling Guide](https://docusaurus.io/docs/swizzling)
- [OpenAI API Docs](https://platform.openai.com/docs/api-reference)
- [React Documentation](https://react.dev)
- [Front-End Book Repository](./../../README.md)

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review error messages in browser console (F12)
3. Refer to API contracts in `contracts/` directory
4. Create an issue in the repository

---

**Happy translating!** 🌐
