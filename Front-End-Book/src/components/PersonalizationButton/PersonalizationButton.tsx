/**
 * PersonalizationButton Component
 *
 * Displays a button that allows authenticated users to personalize chapter content
 * based on their technical background level (beginner/intermediate/advanced).
 *
 * States:
 * - default: "Personalize for Me" button visible
 * - loading: Spinner + "Personalizing..." message
 * - personalized: "Personalized for: [Level]" indicator + toggle to view personalized content
 * - error: Error message + retry option
 *
 * Features:
 * - Markdown rendering using react-markdown
 * - Toggle between original and personalized content
 * - Debounces rapid clicks (300ms)
 * - Stores original content in ref
 * - Smooth state transitions via CSS
 * - ProtectedFeature wrapper for auth protection
 */

import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { usePersonalization } from '../../hooks/usePersonalization';
import { ProtectedFeature } from '../Auth/ProtectedFeature';
import styles from './PersonalizationButton.module.css';

const PersonalizationButton: React.FC = () => {
  const { user } = useAuth();
  const { state, error, personalizationLevel, personalize, resetToOriginal } =
    usePersonalization();
  const [showLevelDialog, setShowLevelDialog] = useState(false);

  // Determine button content based on state
  const getButtonContent = () => {
    switch (state) {
      case 'loading':
        return (
          <>
            <span className={styles.spinner}></span>
            <span className={styles.loadingText}>Personalizing...</span>
          </>
        );
      case 'personalized':
        return (
          <>
            <span className={styles.statusIcon}>✓</span>
            <span>🎯 Reset to Original</span>
          </>
        );
      case 'default':
      default:
        return '🎯 Personalize Content';
    }
  };

  const handleButtonClick = () => {
    if (state === 'personalized') {
      resetToOriginal();
    } else if (state !== 'loading') {
      setShowLevelDialog(true);
    }
  };

  const handleLevelSelect = (level: string) => {
    setShowLevelDialog(false);
    // Pass the level to the personalize function
    personalize(level);
  };

  return (
    <ProtectedFeature customAuthMessage="🎯 Personalize Content - Sign in required" colorScheme="personalization">
      <div className={styles.container}>
        <div className={styles.personalizationBox}>
          <button
            className={`${styles.button} ${styles[state]}`}
            onClick={handleButtonClick}
            disabled={state === 'loading'}
            aria-label={
              state === 'personalized' ? 'Reset to original content' : 'Personalize content for me'
            }
          >
            {getButtonContent()}
          </button>

          {state === 'personalized' && personalizationLevel && (
            <div className={styles.levelIndicator}>
              ✓ Personalized for: <strong>{personalizationLevel}</strong>
            </div>
          )}

          {state === 'error' && error && (
            <div className={styles.errorMessage}>
              <span className={styles.errorIcon}>⚠️</span>
              <span>{error}</span>
              <button
                className={styles.retryLink}
                onClick={handleButtonClick}
                aria-label="Retry personalization"
              >
                Retry
              </button>
            </div>
          )}

          {showLevelDialog && (
            <div className={styles.levelDialog}>
              <div className={styles.levelDialogContent}>
                <h3>Select Your Technical Level</h3>
                <p>Choose your skill level to get personalized content:</p>
                <div className={styles.levelButtons}>
                  <button
                    className={styles.levelButton}
                    onClick={() => handleLevelSelect('beginner')}
                  >
                    🌱 Beginner
                    <span className={styles.levelDescription}>New to the topic</span>
                  </button>
                  <button
                    className={styles.levelButton}
                    onClick={() => handleLevelSelect('intermediate')}
                  >
                    📚 Intermediate
                    <span className={styles.levelDescription}>Some experience</span>
                  </button>
                  <button
                    className={styles.levelButton}
                    onClick={() => handleLevelSelect('advanced')}
                  >
                    🚀 Advanced
                    <span className={styles.levelDescription}>Expert knowledge</span>
                  </button>
                </div>
                <button
                  className={styles.cancelButton}
                  onClick={() => setShowLevelDialog(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </ProtectedFeature>
  );
};

export default PersonalizationButton;
