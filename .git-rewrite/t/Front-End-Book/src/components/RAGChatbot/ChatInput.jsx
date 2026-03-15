import React, { useState } from 'react';
import styles from './styles.module.css';

const MAX_LENGTH = 2000;

/**
 * T063: Chat Input Component
 * Textarea for user input with character counter.
 * Submit on Enter, Shift+Enter for newline.
 */
export default function ChatInput({ onSend, disabled }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && input.length <= MAX_LENGTH) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form className={styles.chatInputForm} onSubmit={handleSubmit}>
      <textarea
        className={styles.chatInput}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Ask a question about the textbook..."
        disabled={disabled}
        maxLength={MAX_LENGTH}
        rows={2}
      />
      <div className={styles.inputFooter}>
        <span className={styles.charCount}>
          {input.length}/{MAX_LENGTH}
        </span>
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className={styles.sendButton}
        >
          Send
        </button>
      </div>
    </form>
  );
}
