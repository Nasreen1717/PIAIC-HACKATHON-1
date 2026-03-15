/**
 * T008: useTranslation React Hook
 *
 * Manages translation state and actions:
 * - Current language (en/ur)
 * - Loading state during translation
 * - Error handling
 * - Preference persistence
 * - Translate and toggle actions
 *
 * Design: Custom hook using React hooks (useState, useEffect, useCallback)
 * Integrates with:
 * - translationApi.ts for API calls
 * - storageManager.ts for preference persistence
 * - contentParser.ts for content extraction
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  UseTranslationReturn,
  TranslationState,
  TranslationPreference,
  TranslationError,
  CodeBlock,
} from './types';
import { translate } from '../../utils/translationApi';
import { getPreference, setPreference } from '../../utils/storageManager';
import { parseChapterContent, hasTranslatableContent, reconstructContent } from '../../utils/contentParser';

/**
 * Check if running in development mode
 * Works in both browser and Node.js contexts
 */
const isDevelopment = (): boolean => {
  if (typeof process !== 'undefined' && process.env?.NODE_ENV === 'development') {
    return true;
  }
  return false;
};

/**
 * useTranslation hook
 *
 * Provides translation functionality and state management.
 * Loads saved preference on mount, manages translation state, persists changes.
 *
 * @returns UseTranslationReturn with state and actions
 */
export function useTranslation(): UseTranslationReturn {
  // State: current language
  const [language, setLanguage] = useState<'en' | 'ur'>('en');

  // State: whether translation is in progress
  const [isLoading, setIsLoading] = useState(false);

  // State: error from translation or storage
  const [error, setError] = useState<TranslationError | null>(null);

  // State: duration of last translation in ms
  const [lastTranslationDuration, setLastTranslationDuration] = useState<number | undefined>();

  // Ref: store original English content for restoration
  const originalContentRef = useRef<string>('');

  // Ref: store article element for later access
  const articleElementRef = useRef<HTMLElement | null>(null);

  // Compute derived state
  const isTranslated = language === 'ur';

  /**
   * Initialize: Always start with English (fresh page load)
   *
   * Each page load resets to English. User's preference to translate
   * is per-page-load, not persisted across page navigations.
   * This ensures the page always displays in English on load.
   */
  useEffect(() => {
    // Always reset to English on mount (new page load)
    setLanguage('en');

    if (isDevelopment()) {
      console.log('[useTranslation] Initialized: language set to English on page load');
    }
  }, []);

  /**
   * Translate content to Urdu
   *
   * Steps:
   * 1. Find and parse article content
   * 2. Call OpenAI API to translate
   * 3. Update DOM with translated text
   * 4. Save preference to localStorage
   * 5. Update state
   *
   * @throws Sets error state on failure
   */
  const translate_action = useCallback(async () => {
    try {
      setError(null);
      setIsLoading(true);

      const startTime = performance.now();

      // Find article element
      const article = document.querySelector('article') as HTMLElement | null;
      if (!article) {
        throw {
          code: 'parse_error',
          message: 'Article element not found',
          retryable: false,
        } as TranslationError;
      }

      articleElementRef.current = article;

      // Check for translatable content
      if (!hasTranslatableContent(article)) {
        throw {
          code: 'parse_error',
          message: 'No content to translate',
          retryable: false,
        } as TranslationError;
      }

      // Parse content (extract translatable text + code blocks)
      const parsed = parseChapterContent(article);

      // Store original content for restoration
      originalContentRef.current = article.innerHTML;

      // Store code blocks for later reference
      const originalCodeBlocks = parsed.codeBlocks;

      if (isDevelopment()) {
        console.log('[useTranslation] Parsed content:', {
          contentLength: parsed.prose.length,
          codeBlocks: originalCodeBlocks.length,
        });
      }

      // Call API to translate prose (code blocks are replaced with placeholders)
      const translatedText = await translate(parsed.prose, 'ur');

      // T014: Reconstruct HTML by restoring code blocks from placeholders
      const reconstructed = reconstructContent(translatedText, originalCodeBlocks);

      // Create temporary container and apply styling classes
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = reconstructed;

      // Add CSS classes to elements for better styling
      // Add class to headings
      tempDiv.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach((el) => {
        el.classList.add('translated-heading');
      });

      // Add class to paragraphs
      tempDiv.querySelectorAll('p').forEach((el) => {
        el.classList.add('translated-paragraph');
      });

      // Add class to lists
      tempDiv.querySelectorAll('ul, ol').forEach((el) => {
        el.classList.add('translated-list');
      });

      // Add class to code blocks
      tempDiv.querySelectorAll('pre, code').forEach((el) => {
        el.classList.add('translated-code');
      });

      // Add class to blockquotes
      tempDiv.querySelectorAll('blockquote').forEach((el) => {
        el.classList.add('translated-blockquote');
      });

      // Add class to images
      tempDiv.querySelectorAll('img').forEach((el) => {
        el.classList.add('translated-image');
      });

      // Add class to tables
      tempDiv.querySelectorAll('table').forEach((el) => {
        el.classList.add('translated-table');
      });

      // Update DOM with translated content (preserving code blocks and styling)
      article.innerHTML = tempDiv.innerHTML;

      const duration = performance.now() - startTime;
      setLastTranslationDuration(duration);

      // Update state
      setLanguage('ur');

      // Save preference
      const saved = setPreference('ur');

      if (isDevelopment()) {
        console.log('[useTranslation] Translation complete', {
          duration: `${duration.toFixed(0)}ms`,
          preferenceSource: saved ? 'localStorage' : 'session',
        });
      }
    } catch (err) {
      const translationError = err as TranslationError;
      setError(translationError);
      setLanguage('en'); // Revert on error

      if (isDevelopment()) {
        console.error('[useTranslation] Translation failed:', translationError);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Revert to English
   *
   * Restores original HTML content from ref and re-applies styling classes.
   * Used when user toggles back to English after translation.
   */
  const revertToEnglish = useCallback(() => {
    try {
      const article = articleElementRef.current || document.querySelector('article');
      if (!article || !originalContentRef.current) {
        console.warn('[useTranslation] Cannot revert: missing article or original content');
        return;
      }

      // Create temporary container
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = originalContentRef.current;

      // Re-apply CSS classes to elements for styling consistency
      // Add class to headings
      tempDiv.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach((el) => {
        el.classList.add('personalized-heading');
      });

      // Add class to paragraphs
      tempDiv.querySelectorAll('p').forEach((el) => {
        el.classList.add('personalized-paragraph');
      });

      // Add class to lists
      tempDiv.querySelectorAll('ul, ol').forEach((el) => {
        el.classList.add('personalized-list');
      });

      // Add class to code blocks
      tempDiv.querySelectorAll('pre, code').forEach((el) => {
        el.classList.add('personalized-code');
      });

      // Add class to blockquotes
      tempDiv.querySelectorAll('blockquote').forEach((el) => {
        el.classList.add('personalized-blockquote');
      });

      // Add class to images
      tempDiv.querySelectorAll('img').forEach((el) => {
        el.classList.add('personalized-image');
      });

      // Add class to tables
      tempDiv.querySelectorAll('table').forEach((el) => {
        el.classList.add('personalized-table');
      });

      article.innerHTML = tempDiv.innerHTML;

      if (isDevelopment()) {
        console.log('[useTranslation] Reverted to English');
      }
    } catch (err) {
      console.error('[useTranslation] Error reverting to English:', err);
      setError({
        code: 'parse_error',
        message: 'Failed to revert to English',
        retryable: true,
      });
    }
  }, []);

  /**
   * Toggle between English and Urdu
   *
   * If current language is English, translate to Urdu.
   * If current language is Urdu, revert to English.
   */
  const toggleLanguage = useCallback(async () => {
    if (language === 'en') {
      // Translate to Urdu
      await translate_action();
    } else {
      // Revert to English
      revertToEnglish();
      setLanguage('en');
      setPreference('en');
      setError(null);
    }
  }, [language, translate_action, revertToEnglish]);

  /**
   * Manual translate action
   * Called from component when user clicks button
   */
  const perform_translation = useCallback(
    async (targetLanguage: 'ur' | 'en' = 'ur') => {
      if (targetLanguage === 'ur') {
        await translate_action();
      } else {
        revertToEnglish();
        setLanguage('en');
      }
    },
    [translate_action, revertToEnglish]
  );

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // State
    language,
    isLoading,
    isTranslated,
    error,

    // Actions
    translate: perform_translation,
    toggleLanguage,
    clearError,

    // Metadata
    lastTranslationDuration,
  };
}

/**
 * Export hook for use in components
 */
export default useTranslation;
