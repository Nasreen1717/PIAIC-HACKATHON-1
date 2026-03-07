/**
 * T066: Root Component (Swizzled)
 * T070: Dark Mode Support
 * T038: TextSelectionHandler Integration
 * **T077**: Use ChatContext.isOpen instead of local state
 * Wraps entire application to provide global chat context and UI.
 * This file is generated via: npm run swizzle @docusaurus/theme-classic Root -- --eject
 */

import React, { useEffect } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { ChatProvider, useChatContext } from '@site/src/context/ChatContext';
import { AuthProvider } from '@site/src/context/AuthContext';
import FloatingButton from '@site/src/components/RAGChatbot/FloatingButton';
import ChatInterface from '@site/src/components/RAGChatbot/ChatInterface';
import TextSelectionHandler from '@site/src/components/RAGChatbot/TextSelectionHandler';
import ErrorBoundary from '@site/src/components/RAGChatbot/ErrorBoundary';

/**
 * Inner Root component that uses ChatContext
 * Separated from outer Root to access ChatContext hooks
 * **T078**: Add logging for debugging state flow
 */
function RootContent({ children }) {
  const { isOpen, dispatch } = useChatContext();
  const { siteConfig } = useDocusaurusContext();

  // Inject OpenAI API key from Docusaurus config into window global for client-side usage
  useEffect(() => {
    if (siteConfig?.customFields?.openaiApiKey) {
      window.__DOCUSAURUS_OPENAI_API_KEY__ = siteConfig.customFields.openaiApiKey;
      console.log('✅ [RootContent] OpenAI API key injected');
    } else {
      console.warn('⚠️ [RootContent] OpenAI API key not found in Docusaurus config');
    }
  }, [siteConfig]);

  console.log('📍 [RootContent] isOpen state:', isOpen);

  const handleOpenChat = () => {
    console.log('📞 [RootContent] handleOpenChat called');
    dispatch({ type: 'SET_IS_OPEN', payload: true });
  };

  const handleCloseChat = () => {
    console.log('📞 [RootContent] handleCloseChat called');
    dispatch({ type: 'SET_IS_OPEN', payload: false });
  };

  const handleToggleChat = () => {
    console.log('📞 [RootContent] handleToggleChat called, isOpen:', isOpen);
    dispatch({ type: 'SET_IS_OPEN', payload: !isOpen });
  };

  return (
    <>
      {children}
      {/* **T038**: Text Selection Handler - detects selected text and shows action button */}
      <TextSelectionHandler />
      <FloatingButton onClick={handleToggleChat} isOpen={isOpen} />
      <ChatInterface
        isOpen={isOpen}
        onClose={handleCloseChat}
      />
      {isOpen && console.log('✅ [RootContent] ChatInterface should be visible (isOpen=true)')}
      {!isOpen && console.log('❌ [RootContent] ChatInterface should be hidden (isOpen=false)')}
    </>
  );
}

// This is the swizzled root that wraps all pages
export default function Root({ children }) {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <ChatProvider>
          <RootContent>{children}</RootContent>
        </ChatProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}
