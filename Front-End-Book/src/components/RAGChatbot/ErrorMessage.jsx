import React from 'react';
import styles from './styles.module.css';

/**
 * T062: Error Message Component
 * Displays error messages with optional retry button.
 */
export default function ErrorMessage({ error, onRetry }) {
  const errorText = error?.message || 'Something went wrong. Please try again.';

  return (
    <div className={styles.errorMessage}>
      <span className={styles.errorIcon}>⚠️</span>
      <div className={styles.errorContent}>
        <p>{errorText}</p>
        {onRetry && (
          <button onClick={onRetry} className={styles.retryButton}>
            Retry
          </button>
        )}
      </div>
    </div>
  );
}
