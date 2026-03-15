import React, { useEffect, useRef } from 'react';
import { useChatContext } from '@site/src/context/ChatContext';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';
import ErrorMessage from './ErrorMessage';
import styles from './styles.module.css';

/**
 * T059: Chat Interface Component
 * Main modal/drawer for chat interaction.
 * Responsive: drawer on mobile, modal on desktop.
 */
export default function ChatInterface({ isOpen, onClose }) {
  const { messages, loading, error, sendMessage } = useChatContext();
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!isOpen) return null;

  return (
    <div className={styles.chatModal}>
      <div className={styles.chatHeader}>
        <h3>AI Tutor</h3>
        <button
          onClick={onClose}
          aria-label="Close chat"
          title="Close chat (Esc)"
        >
          ✕
        </button>
      </div>

      <div className={styles.chatMessages}>
        {messages.length === 0 && (
          <div
            style={{
              textAlign: 'center',
              color: 'var(--ifm-font-color-secondary)',
              fontSize: '13px',
              marginTop: '20px',
            }}
          >
            <p>👋 Welcome to AI Tutor!</p>
            <p style={{ fontSize: '12px' }}>
              Ask any questions about the textbook.
            </p>
          </div>
        )}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        {loading && <TypingIndicator />}
        {error && <ErrorMessage error={error} onRetry={() => {}} />}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSend={sendMessage} disabled={loading} />
    </div>
  );
}
