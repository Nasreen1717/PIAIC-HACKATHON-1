/**
 * T009: TranslationButton Component
 *
 * UI component that allows users to toggle article translation between English and Urdu.
 *
 * Features:
 * - Button to trigger translation
 * - Loading spinner during translation
 * - Error display with retry capability
 * - ARIA labels for accessibility
 * - Uses useTranslation hook for state management
 *
 * Integration: Injected into Docusaurus DocItem/Content component
 */

import React, { useEffect, useState } from 'react';
import useTranslation from './useTranslation';
import { ProtectedFeature } from '@site/src/components/Auth/ProtectedFeature';
import styles from './TranslationButton.module.css';

/**
 * TranslationButton component
 *
 * Renders a button that toggles article translation to Urdu.
 * Displays loading state during translation and errors if translation fails.
 * Requires user to be authenticated to use this feature.
 */
export default function TranslationButton(): JSX.Element {
  const { language, isLoading, error, toggleLanguage, clearError } = useTranslation();
  const [showError, setShowError] = useState(false);

  // Show error for 5 seconds then auto-hide
  useEffect(() => {
    if (error) {
      setShowError(true);
      const timer = setTimeout(() => setShowError(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  const buttonLabel =
    language === 'ur'
      ? '✓ Back to English'
      : '🌐 Urdu Translation is available';

  const buttonAriaLabel =
    language === 'ur'
      ? 'Revert article to English'
      : 'Translate article to Urdu';

  const handleDismissError = () => {
    setShowError(false);
    clearError();
  };

  return (
    <ProtectedFeature customAuthMessage="🌐 Translate to Urdu - Sign in required" colorScheme="translation">
      <div className={styles.container}>
        <button
        className={styles.button}
        onClick={toggleLanguage}
        disabled={isLoading}
        aria-label={buttonAriaLabel}
        title={buttonAriaLabel}
      >
        {isLoading ? (
          <>
            <span className={styles.spinner} aria-hidden="true" />
            <span className={styles.loadingText}>Translating...</span>
          </>
        ) : (
          buttonLabel
        )}
      </button>

      {error && showError && (
        <div className={styles.errorContainer} role="alert">
          <div className={styles.errorMessage}>
            <strong>Translation Error:</strong> {error.message}
          </div>
          <div className={styles.errorActions}>
            {error.retryable && (
              <button
                className={styles.retryButton}
                onClick={() => {
                  setShowError(false);
                  handleDismissError();
                  // Wait a moment then retry by toggling again
                  setTimeout(() => toggleLanguage(), 200);
                }}
                aria-label="Retry translation"
              >
                Retry
              </button>
            )}
            <button
              className={styles.dismissButton}
              onClick={handleDismissError}
              aria-label="Dismiss error message"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}
      </div>
    </ProtectedFeature>
  );
}
