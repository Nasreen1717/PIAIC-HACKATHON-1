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
 */
function chatReducer(state, action) {
  switch (action.type) {
    case ACTIONS.SET_SESSION:
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
      return { ...state, selectedText: action.payload.selected_text, selectedContext: action.payload };
    case ACTIONS.SET_IS_OPEN:
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
        // Try to load session from localStorage
        let sessionId = localStorage.getItem('chatSessionId');

        if (!sessionId) {
          // Create new session
          const session = await createSession();
          sessionId = session.session_id;
          localStorage.setItem('chatSessionId', sessionId);
        }

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
   * @param {string} question - User's question
   * @param {string} selectedText - Optional selected text from page
   */
  const sendMessage = async (question, selectedText = null) => {
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

      const response = await sendChatMessage(
        {
          question,
          session_id: state.sessionId,
          selected_text: selectedText,
        },
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
