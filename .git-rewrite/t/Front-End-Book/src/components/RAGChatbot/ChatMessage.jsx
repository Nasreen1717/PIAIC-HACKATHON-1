import React from 'react';
import CitationLink from './CitationLink';
import AnswerWithCitations from './AnswerWithCitations';
import styles from './styles.module.css';

/**
 * T060: Chat Message Component
 * Displays individual messages with timestamps and citations.
 * Different styling for user vs assistant messages.
 *
 * Uses AnswerWithCitations to parse and linkify inline citations
 * in assistant responses.
 */
export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  // Format timestamp
  const timestamp = new Date(message.created_at).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div
      className={`${styles.message} ${
        isUser ? styles.userMessage : styles.assistantMessage
      }`}
    >
      <div className={styles.messageHeader}>
        <span className={styles.role}>{isUser ? 'You' : 'AI Tutor'}</span>
        <span className={styles.timestamp}>{timestamp}</span>
      </div>

      {/* Show answer with parsed inline citations for assistant messages */}
      {!isUser ? (
        <AnswerWithCitations answer={message.content} />
      ) : (
        <div className={styles.messageContent}>{message.content}</div>
      )}

      {!isUser && message.citations && message.citations.length > 0 && (
        <div className={styles.citations}>
          <span className={styles.citationsLabel}>Sources:</span>
          {message.citations.map((citation, idx) => (
            <CitationLink key={idx} citation={citation} />
          ))}
        </div>
      )}
    </div>
  );
}
