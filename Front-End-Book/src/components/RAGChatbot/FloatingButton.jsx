import React from 'react';
import styles from './styles.module.css';

/**
 * T058: Floating Button Component
 * Toggles chat interface when clicked.
 * Shows 💬 when closed, ✕ when open.
 * Fixed position in bottom-left corner of screen.
 */
export default function FloatingButton({ onClick, isOpen = false, unreadCount = 0 }) {
  return (
    <button
      className={styles.floatingButton}
      onClick={onClick}
      aria-label={isOpen ? "Close chat assistant" : "Open chat assistant"}
      title={isOpen ? "Close AI Tutor (or press Esc)" : "Open AI Tutor"}
    >
      <span className={styles.icon}>
        {isOpen ? '✕' : '💬'}
      </span>
      {unreadCount > 0 && !isOpen && (
        <span className={styles.badge}>{unreadCount}</span>
      )}
    </button>
  );
}
