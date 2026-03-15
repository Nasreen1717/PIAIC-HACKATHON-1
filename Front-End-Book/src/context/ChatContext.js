import React, { createContext, useContext, useReducer, useEffect } from 'react';
import {
  sendChatMessage,
  fetchConversationHistory,
  createSession,
} from '@site/src/utils/chatApi';

/**
 * T073: Chat Context
 * T074: localStorage Persistence
 * Global state management for chat interface using React Context + useReducer
 */

export const ChatContext = createContext();

// Action types
const ACTIONS = {
  SET_SESSION: 'SET_SESSION',
  SET_MESSAGES: 'SET_MESSAGES',
  ADD_MESSAGE: 'ADD_MESSAGE',
  UPDATE_MESSAGE: 'UPDATE_MESSAGE',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  SET_SELECTED_TEXT: 'SET_SELECTED_TEXT',
  SET_IS_OPEN: 'SET_IS_OPEN',
};

// Initial state
const initialState = {
  messages: [],
  sessionId: null,
  loading: false,
  error: null,
  initialized: false,
  selectedText: null,
  selectedContext: null,
  isOpen: false,
};

/**
 * Reducer for chat state
 * **T078**: Add logging for debugging state changes
 */
function chatReducer(state, action) {
  console.log('🔄 [ChatReducer] Action received:', action.type, action.payload);

  switch (action.type) {
    case ACTIONS.SET_SESSION:
      console.log('📊 [ChatReducer] Setting session:', action.payload);
      return { ...state, sessionId: action.payload };
    case ACTIONS.SET_MESSAGES:
      return { ...state, messages: action.payload };
    case ACTIONS.ADD_MESSAGE:
      return { ...state, messages: [...state.messages, action.payload] };
    case ACTIONS.UPDATE_MESSAGE:
      return {
        ...state,
        messages: state.messages.map((msg) =>
          msg.id === action.payload.id ? { ...msg, ...action.payload.updates } : msg
        ),
      };
    case ACTIONS.SET_LOADING:
      return { ...state, loading: action.payload };
    case ACTIONS.SET_ERROR:
      return { ...state, error: action.payload, loading: false };
    case ACTIONS.CLEAR_ERROR:
      return { ...state, error: null };
    case ACTIONS.SET_SELECTED_TEXT:
      console.log('📝 [ChatReducer] SET_SELECTED_TEXT received:', action.payload.selected_text?.substring(0, 50));
      return { ...state, selectedText: action.payload.selected_text, selectedContext: action.payload };
    case ACTIONS.SET_IS_OPEN:
      console.log('💬 [ChatReducer] SET_IS_OPEN to:', action.payload);
      return { ...state, isOpen: action.payload };
    default:
      return state;
  }
}

/**
 * Chat Provider Component
 * Wraps application to provide chat state and functions
 */
export function ChatProvider({ children }) {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  // Initialize session on mount
  useEffect(() => {
    const initSession = async () => {
      try {
        // Always create a new session on app load (do not reuse cached sessions)
        // This ensures old chat history doesn't persist across page refreshes
        const session = await createSession();
        const sessionId = session.session_id;

        dispatch({ type: ACTIONS.SET_SESSION, payload: sessionId });

        // Load conversation history
        try {
          const history = await fetchConversationHistory(sessionId);
          dispatch({
            type: ACTIONS.SET_MESSAGES,
            payload: history.messages || [],
          });
        } catch (error) {
          console.warn('Failed to load conversation history:', error.message);
          // Continue without history
        }
      } catch (error) {
        console.error('Failed to initialize chat session:', error.message);
        dispatch({
          type: ACTIONS.SET_ERROR,
          payload: error,
        });
      }
    };

    initSession();
  }, []);

  /**
   * Send message to backend and update local state
   * Uses state.selectedText and state.selectedContext if available
   * @param {string} question - User's question
   */
  const sendMessage = async (question) => {
    if (!question.trim() || !state.sessionId) {
      return;
    }

    // Add user message immediately to UI
    const userMessage = {
      id: `msg_${Date.now()}_${Math.random()}`,
      role: 'user',
      content: question,
      created_at: new Date().toISOString(),
    };
    dispatch({ type: ACTIONS.ADD_MESSAGE, payload: userMessage });

    // Create assistant message placeholder for streaming
    const assistantMessageId = `msg_${Date.now()}_response`;
    const assistantMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      citations: [],
      created_at: new Date().toISOString(),
    };
    dispatch({ type: ACTIONS.ADD_MESSAGE, payload: assistantMessage });

    dispatch({ type: ACTIONS.SET_LOADING, payload: true });
    dispatch({ type: ACTIONS.CLEAR_ERROR });

    try {
      // Call API with streaming callback
      let currentContent = '';
      let currentCitations = [];

      // Build request with selected text context if available
      const requestPayload = {
        question,
        session_id: state.sessionId,
      };

      // Include selected text and context if available in state
      // Use state values as the source of truth (they persist across multiple questions)
      if (state.selectedText && state.selectedContext) {
        console.log('📨 [sendMessage] Including selected_text in request:', state.selectedText.substring(0, 50));
        requestPayload.selected_text = state.selectedText;
        requestPayload.chapter_path = state.selectedContext.chapter_path;
        requestPayload.section_id = state.selectedContext.section_id;
        requestPayload.section_title = state.selectedContext.section_title;
        requestPayload.context_before = state.selectedContext.context_before;
        requestPayload.context_after = state.selectedContext.context_after;
      } else {
        console.log('📨 [sendMessage] No selected_text in state, using vector search');
      }

      console.log('📨 [sendMessage] Request payload:', JSON.stringify(requestPayload, null, 2).substring(0, 200));

      const response = await sendChatMessage(
        requestPayload,
        (chunk) => {
          if (chunk.type === 'text') {
            // Update message content as text arrives
            currentContent += chunk.delta;
            dispatch({
              type: ACTIONS.UPDATE_MESSAGE,
              payload: {
                id: assistantMessageId,
                updates: {
                  content: currentContent,
                },
              },
            });
          } else if (chunk.type === 'citation') {
            // Add citation to message
            currentCitations.push(chunk.data);
            dispatch({
              type: ACTIONS.UPDATE_MESSAGE,
              payload: {
                id: assistantMessageId,
                updates: {
                  citations: currentCitations,
                },
              },
            });
          }
        }
      );

      // Final update with complete response
      dispatch({
        type: ACTIONS.UPDATE_MESSAGE,
        payload: {
          id: assistantMessageId,
          updates: {
            content: response.answer,
            citations: response.citations || [],
          },
        },
      });

      // NOTE: Selection is intentionally NOT cleared after use
      // This allows follow-up questions to continue using the same selected text context
      // User can manually clear via SelectedTextBanner clear button if needed
    } catch (error) {
      console.error('Chat error:', error);
      dispatch({
        type: ACTIONS.SET_ERROR,
        payload: error,
      });
    } finally {
      dispatch({ type: ACTIONS.SET_LOADING, payload: false });
    }
  };

  /**
   * Clear conversation history and create new session
   */
  const clearHistory = async () => {
    try {
      const session = await createSession();
      const newSessionId = session.session_id;
      localStorage.setItem('chatSessionId', newSessionId);
      dispatch({ type: ACTIONS.SET_SESSION, payload: newSessionId });
      dispatch({ type: ACTIONS.SET_MESSAGES, payload: [] });
      dispatch({ type: ACTIONS.CLEAR_ERROR });
    } catch (error) {
      console.error('Failed to clear history:', error.message);
      dispatch({
        type: ACTIONS.SET_ERROR,
        payload: error,
      });
    }
  };

  const value = {
    ...state,
    sendMessage,
    clearHistory,
    dismissError: () => dispatch({ type: ACTIONS.CLEAR_ERROR }),
    dispatch, // Expose dispatch for direct action dispatching
  };

  return (
    <ChatContext.Provider value={value}>{children}</ChatContext.Provider>
  );
}

/**
 * Hook to use Chat Context
 * Must be called within ChatProvider
 */
export function useChatContext() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within ChatProvider');
  }
  return context;
}
