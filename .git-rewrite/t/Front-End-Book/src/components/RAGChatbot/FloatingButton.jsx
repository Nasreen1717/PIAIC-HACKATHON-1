import React from 'react';
import styles from './styles.module.css';

/**
 * T058: Floating Button Component
 * Opens chat interface when clicked.
 * Fixed position in bottom-right corner of screen.
 */
export default function FloatingButton({ onClick, unreadCount = 0 }) {
  return (
    <button
      className={styles.floatingButton}
      onClick={onClick}
      aria-label="Open chat assistant"
      title="Open AI Tutor"
    >
      <span className={styles.icon}>💬</span>
      {unreadCount > 0 && (
        <span className={styles.badge}>{unreadCount}</span>
      )}
    </button>
  );
}
