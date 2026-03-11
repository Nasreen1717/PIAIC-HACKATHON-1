/**
 * T005: Translation API Wrapper
 *
 * Provides translate() function to call backend /api/v1/translate endpoint
 * with JWT authentication. Includes:
 * - JWT token from AuthContext
 * - Retry logic with exponential backoff
 * - Proper error handling and categorization
 * - Performance timing
 */

import { TranslationError } from '../components/TranslationButton/types';

/**
 * Get JWT token from localStorage
 * Set by AuthContext during signin/signup
 */
function getJWTToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

/**
 * Sleep utility for backoff delays
 */
const sleep = (ms: number): Promise<void> =>
  new Promise(resolve => setTimeout(resolve, ms));

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
 * Map HTTP errors to TranslationError
 */
function mapHTTPError(status: number, message: string): TranslationError {
  if (status === 401) {
    return {
      code: 'auth_error',
      message: 'Session expired. Please sign in again.',
      retryable: false,
    };
  } else if (status === 400) {
    return {
      code: 'validation_error',
      message: message || 'Invalid request',
      retryable: false,
    };
  } else if (status === 503) {
    return {
      code: 'api_error',
      message: 'Translation service unavailable. Please try again later.',
      retryable: true,
    };
  } else if (status >= 500) {
    return {
      code: 'api_error',
      message: 'Server error. Please try again.',
      retryable: true,
    };
  }

  return {
    code: 'network_error',
    message: 'Network error. Please check your connection.',
    retryable: true,
  };
}

/**
 * Translate content via protected backend endpoint
 *
 * @param content - English text to translate
 * @param targetLanguage - Target language (currently only 'ur' for Urdu)
 * @param maxRetries - Maximum number of retry attempts (default: 3)
 * @returns Promise<string> - Translated Urdu text
 * @throws TranslationError on API or validation failure
 */
export async function translate(
  content: string,
  targetLanguage: 'ur' = 'ur',
  maxRetries: number = 3
): Promise<string> {
  // Validate input
  if (!content || !content.trim()) {
    throw {
      code: 'parse_error',
      message: 'No content to translate',
      retryable: false,
    } as TranslationError;
  }

  // Get JWT token - required for authentication
  const token = getJWTToken();
  if (!token) {
    throw {
      code: 'auth_error',
      message: 'Not authenticated. Please sign in to use translation.',
      retryable: false,
    } as TranslationError;
  }

  // Retry loop with exponential backoff
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const startTime = performance.now();

      console.log(`[Translation] Attempt ${attempt}/${maxRetries} - Calling /api/v1/translate...`, {
        contentLength: content.length,
        targetLanguage,
      });

      const apiUrl =
        typeof process !== 'undefined' && process.env?.REACT_APP_API_URL
          ? process.env.REACT_APP_API_URL
          : 'http://localhost:8000';

      const response = await fetch(`${apiUrl}/api/v1/translate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          text: content,
          target_lang: targetLanguage,
        }),
      });

      const duration = performance.now() - startTime;

      // Handle non-OK responses
      if (!response.ok) {
        let errorDetail = 'Unknown error';
        try {
          const errorData = await response.json();
          errorDetail = errorData.detail || errorDetail;
        } catch {
          // Ignore parse errors for error responses
        }

        // 401 means auth failed - don't retry
        if (response.status === 401) {
          localStorage.removeItem('auth_token');
          localStorage.removeItem('auth_user');
          throw mapHTTPError(response.status, 'Session expired');
        }

        throw mapHTTPError(response.status, errorDetail);
      }

      const data = await response.json();

      if (!data.translated_text) {
        throw {
          code: 'parse_error',
          message: 'Invalid response from translation service',
          retryable: true,
        } as TranslationError;
      }

      // Log performance metrics in development
      if (isDevelopment()) {
        console.log('[Translation] Success', {
          duration: `${duration.toFixed(0)}ms`,
          confidence: data.confidence,
        });
      }

      return data.translated_text;
    } catch (error: any) {
      // Check if error is retryable
      const isRetryable = error.retryable !== false && error.code !== 'auth_error' && error.code !== 'parse_error';

      // If not retryable or last attempt, throw error
      if (!isRetryable || attempt === maxRetries) {
        console.error('[Translation] Final error after all retries:', {
          code: error.code,
          message: error.message,
        });
        throw error;
      }

      // Calculate exponential backoff: 1s, 2s, 4s, etc.
      const delayMs = 1000 * Math.pow(2, attempt - 1);

      console.warn(`[Translation] Attempt ${attempt} failed, retrying in ${delayMs}ms`, {
        error: error.message,
      });

      await sleep(delayMs);
    }
  }

  // This should never be reached due to the throw in the loop
  throw {
    code: 'unknown',
    message: 'Translation failed after maximum retries',
    retryable: false,
  } as TranslationError;
}

/**
 * Check if user is authenticated
 * Useful for validating setup before attempting translations
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('auth_token');
}
