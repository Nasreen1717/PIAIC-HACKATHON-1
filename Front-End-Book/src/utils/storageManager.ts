/**
 * T007: Storage Manager for Translation Preferences
 *
 * Provides abstraction over localStorage with graceful fallback to session-only storage.
 * Handles:
 * - localStorage availability detection
 * - Error recovery (quota exceeded, privacy mode, etc.)
 * - Automatic fallback to in-memory session storage
 * - Preference persistence with timestamps
 *
 * Design: Factory pattern with strategy switching (localStorage → session-only)
 */

import { TranslationPreference } from '../components/TranslationButton/types';

const STORAGE_KEY_PREFIX = 'urdu_translation_';
const PREFERENCE_KEY = `${STORAGE_KEY_PREFIX}preference`;
const SESSION_STORAGE_KEY = `${STORAGE_KEY_PREFIX}session`;

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
 * In-memory fallback storage for when localStorage is unavailable
 * Persists for session duration only
 */
const sessionStorage = new Map<string, string>();

/**
 * Detect if localStorage is available and functional
 *
 * Browsers in private/incognito mode or restrictive CSP environments
 * may throw on localStorage access. Test with actual write/read.
 */
function isLocalStorageAvailable(): boolean {
  try {
    const testKey = `${STORAGE_KEY_PREFIX}test_${Date.now()}`;
    const testValue = 'test';

    // Try write
    window.localStorage.setItem(testKey, testValue);

    // Try read
    const retrieved = window.localStorage.getItem(testKey);

    // Try delete
    window.localStorage.removeItem(testKey);

    return retrieved === testValue;
  } catch (error) {
    // Quota exceeded, security error, or feature disabled
    console.warn('[StorageManager] localStorage not available:', error);
    return false;
  }
}

/**
 * Save preference to localStorage or session
 *
 * @param language - 'en' or 'ur'
 * @returns boolean - true if saved to localStorage, false if fallback to session
 */
export function setPreference(language: 'en' | 'ur'): boolean {
  const preference: TranslationPreference = {
    language,
    savedAt: new Date().toISOString(),
    source: 'localStorage',
  };

  const preferenceString = JSON.stringify(preference);

  try {
    if (isLocalStorageAvailable()) {
      window.localStorage.setItem(PREFERENCE_KEY, preferenceString);
      preference.source = 'localStorage';
      return true;
    }
  } catch (error) {
    console.warn('[StorageManager] Failed to save to localStorage:', error);
  }

  // Fallback to session storage
  try {
    sessionStorage.set(PREFERENCE_KEY, preferenceString);
    preference.source = 'session';
    return false; // Indicates fallback
  } catch (error) {
    console.error('[StorageManager] Failed to save to session storage:', error);
    return false;
  }
}

/**
 * Load preference from localStorage or session
 *
 * Returns default (English) if no preference found or on error.
 *
 * @returns TranslationPreference with loaded language or default 'en'
 */
export function getPreference(): TranslationPreference {
  const defaultPreference: TranslationPreference = {
    language: 'en',
    savedAt: new Date().toISOString(),
    source: 'localStorage',
  };

  try {
    // Try localStorage first
    if (isLocalStorageAvailable()) {
      const stored = window.localStorage.getItem(PREFERENCE_KEY);
      if (stored) {
        const preference = JSON.parse(stored) as TranslationPreference;
        // Validate structure
        if (preference.language && (preference.language === 'en' || preference.language === 'ur')) {
          return preference;
        }
      }
    }

    // Try session storage
    const sessionStored = sessionStorage.get(PREFERENCE_KEY);
    if (sessionStored) {
      const preference = JSON.parse(sessionStored) as TranslationPreference;
      if (preference.language && (preference.language === 'en' || preference.language === 'ur')) {
        return preference;
      }
    }
  } catch (error) {
    console.warn('[StorageManager] Error loading preference, using default:', error);
  }

  return defaultPreference;
}

/**
 * Clear preference from both localStorage and session
 *
 * @returns boolean - true if cleared from localStorage, false otherwise
 */
export function clearPreference(): boolean {
  let clearedFromLocalStorage = false;

  try {
    if (isLocalStorageAvailable()) {
      window.localStorage.removeItem(PREFERENCE_KEY);
      clearedFromLocalStorage = true;
    }
  } catch (error) {
    console.warn('[StorageManager] Error clearing localStorage:', error);
  }

  try {
    sessionStorage.delete(PREFERENCE_KEY);
  } catch (error) {
    console.warn('[StorageManager] Error clearing session storage:', error);
  }

  return clearedFromLocalStorage;
}

/**
 * Check if preference exists in storage
 *
 * @returns boolean - true if preference found, false otherwise
 */
export function hasPreference(): boolean {
  try {
    if (isLocalStorageAvailable()) {
      if (window.localStorage.getItem(PREFERENCE_KEY)) {
        return true;
      }
    }

    if (sessionStorage.has(PREFERENCE_KEY)) {
      return true;
    }
  } catch (error) {
    console.warn('[StorageManager] Error checking preference:', error);
  }

  return false;
}

/**
 * Get storage info for debugging/display
 *
 * Useful for showing user whether preference is persisted or session-only.
 */
export function getStorageInfo(): {
  available: boolean;
  source: 'localStorage' | 'session' | 'none';
  message: string;
} {
  if (isLocalStorageAvailable()) {
    return {
      available: true,
      source: 'localStorage',
      message: 'Preferences will be saved permanently',
    };
  }

  if (typeof window !== 'undefined') {
    return {
      available: true,
      source: 'session',
      message: 'Preferences will be saved for this session only (private mode detected)',
    };
  }

  return {
    available: false,
    source: 'none',
    message: 'Storage not available',
  };
}

/**
 * Watch for storage changes (from other tabs/windows)
 *
 * Useful for syncing preference across browser tabs.
 *
 * @param callback - Function called when preference changes in another tab
 * @returns Unsubscribe function to remove listener
 */
export function watchPreferenceChanges(
  callback: (preference: TranslationPreference) => void
): () => void {
  const handler = (event: StorageEvent) => {
    if (event.key === PREFERENCE_KEY && event.newValue) {
      try {
        const preference = JSON.parse(event.newValue) as TranslationPreference;
        callback(preference);
      } catch (error) {
        console.warn('[StorageManager] Error parsing storage change event:', error);
      }
    }
  };

  window.addEventListener('storage', handler);

  // Return unsubscribe function
  return () => {
    window.removeEventListener('storage', handler);
  };
}

/**
 * Debug utility: Log current storage state
 * Only in development mode
 */
export function debugStorageState(): void {
  if (!isDevelopment()) return;

  const info = getStorageInfo();
  const preference = getPreference();

  console.log('[StorageManager] Current state:', {
    storageInfo: info,
    preference,
  });
}

/**
 * Initialize storage manager (detect availability on load)
 *
 * Can be called on app startup to log storage capabilities.
 */
export function initializeStorage(): void {
  const info = getStorageInfo();

  if (isDevelopment()) {
    console.log('[StorageManager] Initialized with:', info.message);
  }
}
