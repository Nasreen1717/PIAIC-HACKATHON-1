/**
 * T016: TranslationButton Error Boundary
 *
 * React Error Boundary to catch errors in the TranslationButton component tree.
 * Provides graceful error handling and recovery mechanism.
 *
 * Features:
 * - Catches rendering errors in TranslationButton and children
 * - Displays user-friendly fallback UI
 * - Logs errors to console for debugging
 * - Provides "reload" button for recovery
 */

import React, { Component, ReactNode, ErrorInfo } from 'react';
import styles from './TranslationButton.module.css';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

/**
 * Error Boundary component for TranslationButton
 *
 * Catches errors during rendering and provides a fallback UI.
 * If TranslationButton crashes, the page continues to work.
 */
export class TranslationErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  /**
   * Update state when an error is caught
   */
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  /**
   * Log error details for debugging
   */
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('[TranslationButton] Error caught by boundary:', error, errorInfo);
  }

  /**
   * Handler for reload button
   */
  handleReload = () => {
    this.setState({ hasError: false, error: undefined });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className={styles.container}>
          <div className={styles.errorContainer} role="alert">
            <div className={styles.errorMessage}>
              <strong>Translation feature unavailable</strong>
            </div>
            <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem' }}>
              An unexpected error occurred. The article is still readable.
            </p>
            <div className={styles.errorActions}>
              <button
                className={styles.retryButton}
                onClick={this.handleReload}
                aria-label="Reload translation feature"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default TranslationErrorBoundary;
