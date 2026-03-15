import React from 'react';
import styles from './styles.module.css';

/**
 * T061: Typing Indicator Component
 * Shows animated dots when AI is generating a response.
 */
export default function TypingIndicator() {
  return (
    <div className={styles.typingIndicator}>
      <span className={styles.dot}></span>
      <span className={styles.dot}></span>
      <span className={styles.dot}></span>
    </div>
  );
}
