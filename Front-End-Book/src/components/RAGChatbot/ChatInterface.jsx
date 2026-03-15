import React, { useEffect, useRef } from 'react';
import { useChatContext } from '@site/src/context/ChatContext';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';
import ErrorMessage from './ErrorMessage';
import SelectedTextBanner from './SelectedTextBanner';
import styles from './styles.module.css';

/**
 * T059: Chat Interface Component
 * Main modal/drawer for chat interaction.
 * Responsive: drawer on mobile, modal on desktop.
 * **T078**: Add logging for debugging visibility
 */
export default function ChatInterface({ isOpen, onClose }) {
  const { messages, loading, error, sendMessage } = useChatContext();
  const messagesEndRef = useRef(null);

  console.log('👁️  [ChatInterface] Rendering with isOpen:', isOpen);

  // Handle Escape key to close chat
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        console.log('🔑 [ChatInterface] Escape key pressed, closing chat');
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      return () => document.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, onClose]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!isOpen) {
    console.log('❌ [ChatInterface] isOpen is false, returning null');
    return null;
  }

  console.log('✅ [ChatInterface] isOpen is true, rendering modal');

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

      <SelectedTextBanner />

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
