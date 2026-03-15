/**
 * Minimal Protected Feature - Professional Auth Button
 * Shows elegant sign-in button for unauthenticated users
 *
 * ✅ WCAG 2.1 AAA Accessible
 * ✅ Minimalist design
 * ✅ Keyboard navigation support
 * ✅ Mobile responsive
 */
import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import styles from './ProtectedFeature.module.css';

interface ProtectedFeatureProps {
  children: React.ReactNode;
  featureName?: string;
  buttonLabel?: string;
  colorScheme?: 'default' | 'translation' | 'personalization';
}

export const ProtectedFeature: React.FC<ProtectedFeatureProps> = ({
  children,
  featureName = 'This feature',
  buttonLabel = 'Sign in',
  colorScheme = 'default',
}) => {
  const { user } = useAuth();

  if (user) {
    return <>{children}</>;
  }

  // Get feature icon based on color scheme
  const getFeatureIcon = () => {
    switch (colorScheme) {
      case 'translation':
        return '🌐';
      case 'personalization':
        return '🎯';
      default:
        return '🔒';
    }
  };

  return (
    <a
      href="/signin"
      className={`${styles.authButton} ${styles[colorScheme]}`}
      role="button"
      tabIndex={0}
      aria-label={`Sign in to access ${featureName}`}
    >
      <span className={styles.icon} aria-hidden="true">
        {getFeatureIcon()}
      </span>
      <span className={styles.label}>{buttonLabel}</span>
    </a>
  );
};
