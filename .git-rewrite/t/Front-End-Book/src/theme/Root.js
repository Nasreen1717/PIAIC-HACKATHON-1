/**
 * T066: Root Component (Swizzled)
 * T070: Dark Mode Support
 * T038: TextSelectionHandler Integration
 * Wraps entire application to provide global chat context and UI.
 * This file is generated via: npm run swizzle @docusaurus/theme-classic Root -- --eject
 */

import React, { useState } from 'react';
import { ChatProvider } from '@site/src/context/ChatContext';
import FloatingButton from '@site/src/components/RAGChatbot/FloatingButton';
import ChatInterface from '@site/src/components/RAGChatbot/ChatInterface';
import TextSelectionHandler from '@site/src/components/RAGChatbot/TextSelectionHandler';
import ErrorBoundary from '@site/src/components/RAGChatbot/ErrorBoundary';

// This is the swizzled root that wraps all pages
export default function Root({ children }) {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <ErrorBoundary>
      <ChatProvider>
        {children}
        {/* **T038**: Text Selection Handler - detects selected text and shows action button */}
        <TextSelectionHandler />
        <FloatingButton onClick={() => setIsChatOpen(true)} />
        <ChatInterface
          isOpen={isChatOpen}
          onClose={() => setIsChatOpen(false)}
        />
      </ChatProvider>
    </ErrorBoundary>
  );
}
