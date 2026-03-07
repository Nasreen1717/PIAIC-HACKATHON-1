/**
 * T004: TypeScript Type Definitions for Urdu Translation Feature
 *
 * Defines all types used across the translation feature:
 * - TranslationPreference: User's language preference (en/ur)
 * - TranslationState: Current translation state (loading, error, content)
 * - TranslationError: Typed errors from API/storage
 * - TranslationResponse: OpenAI API response format
 * - CodeBlock: Extracted code blocks to preserve
 */

/**
 * User's saved language preference
 */
export interface TranslationPreference {
  /** Current selected language: 'en' (English) or 'ur' (Urdu) */
  language: 'en' | 'ur';

  /** ISO8601 timestamp of when preference was last updated */
  savedAt: string;

  /** Where the preference is stored */
  source: 'localStorage' | 'session';
}

/**
 * Current state of translation operation
 */
export interface TranslationState {
  /** Current language of displayed content */
  language: 'en' | 'ur';

  /** Whether a translation is in progress */
  isLoading: boolean;

  /** Whether current content is translated (true if language is 'ur') */
  isTranslated: boolean;

  /** Error that occurred during translation, if any */
  error: TranslationError | null;

  /** Translated content (empty if not translated) */
  translatedText: string;

  /** Duration of last translation in milliseconds */
  lastTranslationDuration?: number;
}

/**
 * Structured error type for translation operations
 */
export interface TranslationError {
  /** Error code: 'api_error', 'storage_error', 'parse_error', 'timeout' */
  code: 'api_error' | 'storage_error' | 'parse_error' | 'timeout' | 'unknown';

  /** Human-readable error message */
  message: string;

  /** Original error object if available */
  originalError?: Error;

  /** Whether user can retry */
  retryable: boolean;
}

/**
 * Response from OpenAI API
 */
export interface TranslationResponse {
  /** Translated text content */
  translatedText: string;

  /** Tokens used in the request */
  tokensUsed: number;

  /** Model used for translation */
  model: string;

  /** Timestamp of translation */
  translatedAt: string;
}

/**
 * Code block extracted from chapter content
 * Code blocks should NOT be translated
 */
export interface CodeBlock {
  /** Unique identifier for this code block */
  id: string;

  /** Programming language (python, bash, javascript, etc.) */
  language: string;

  /** The actual code content (NOT translated) */
  code: string;

  /** Optional metadata about the code block */
  metadata?: {
    /** Optional filename or label for the code */
    filename?: string;

    /** Whether syntax highlighting has been applied */
    highlighted?: boolean;
  };
}

/**
 * Parsed chapter content with translatable sections
 */
export interface ChapterContent {
  /** Unique chapter identifier (from URL or filename) */
  id: string;

  /** Chapter title (translatable) */
  title: string;

  /** Main content sections */
  sections: Section[];

  /** Code blocks extracted from content (NOT translatable) */
  codeBlocks: CodeBlock[];

  /** Metadata about the chapter */
  metadata: {
    /** Module number (1-4) */
    module: number;

    /** Chapter number within module */
    chapter: number;

    /** Current language of displayed content */
    language: 'en' | 'ur';

    /** ISO8601 timestamp of when translation was applied */
    translatedAt?: string;
  };
}

/**
 * A section of chapter content (heading + prose)
 */
export interface Section {
  /** Unique section identifier (e.g., "section-1-1") */
  id: string;

  /** Section heading text (translatable) */
  heading: string;

  /** Paragraph text (translatable) */
  prose: string;

  /** List items if this section contains a list (translatable) */
  listItems?: string[];

  /** Links within this section */
  links?: Array<{
    /** Link text (translatable) */
    text: string;

    /** URL (NOT translatable) */
    href: string;
  }>;
}

/**
 * Props for TranslationButton component
 */
export interface TranslationButtonProps {
  /** Optional: CSS selector for article element to translate */
  articleSelector?: string;

  /** Optional: callback when translation starts */
  onTranslationStart?: () => void;

  /** Optional: callback when translation completes */
  onTranslationComplete?: (success: boolean) => void;

  /** Optional: custom error handler */
  onError?: (error: TranslationError) => void;

  /** Optional: disable button for specific pages */
  disabled?: boolean;
}

/**
 * Return type from useTranslation hook
 */
export interface UseTranslationReturn {
  // State
  /** Current language ('en' or 'ur') */
  language: 'en' | 'ur';

  /** Whether a translation is in progress */
  isLoading: boolean;

  /** Whether current content is translated */
  isTranslated: boolean;

  /** Current error, if any */
  error: TranslationError | null;

  // Actions
  /** Translate content to target language */
  translate: (targetLanguage: 'ur' | 'en') => Promise<void>;

  /** Toggle between English and Urdu */
  toggleLanguage: () => Promise<void>;

  /** Clear any error state */
  clearError: () => void;

  // Metadata
  /** Duration of last translation in milliseconds */
  lastTranslationDuration?: number;
}

/**
 * Parsed content ready for translation
 */
export interface ParsedContent {
  /** Translatable prose content */
  prose: string;

  /** Code blocks that should NOT be translated */
  codeBlocks: CodeBlock[];

  /** Original HTML element for reference */
  originalElement: HTMLElement;
}
