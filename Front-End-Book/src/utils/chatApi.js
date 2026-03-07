/**
 * T071: Chat API Client
 * T072: Retry Logic with Exponential Backoff
 * Provides API methods for chat interaction with timeout and retry handling.
 */

const API_BASE_URL =
  typeof process !== 'undefined' && process.env?.REACT_APP_API_URL
    ? process.env.REACT_APP_API_URL
    : 'http://localhost:8000';
const TIMEOUT_MS = 15000;
const MAX_RETRIES = 3;

/**
 * Custom error class for API errors
 */
class ChatAPIError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
    this.name = 'ChatAPIError';
  }
}

/**
 * Fetch with timeout support
 */
async function fetchWithTimeout(url, options = {}, timeout = TIMEOUT_MS) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new ChatAPIError('Request timeout', 408, null);
    }
    throw error;
  }
}

/**
 * Retry wrapper with exponential backoff
 * Retries on network errors and 5xx errors
 * Does not retry on 4xx client errors
 */
async function fetchWithRetry(
  fn,
  maxAttempts = MAX_RETRIES,
  name = 'API Call'
) {
  let lastError;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Don't retry on client errors (4xx)
      if (error.status >= 400 && error.status < 500) {
        throw error;
      }

      // Don't retry on last attempt
      if (attempt < maxAttempts) {
        const delay = Math.pow(2, attempt - 1) * 1000; // 1s, 2s, 4s
        console.warn(
          `${name} attempt ${attempt} failed. Retrying in ${delay}ms...`,
          error.message
        );
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  console.error(
    `${name} failed after ${maxAttempts} attempts:`,
    lastError.message
  );
  throw lastError;
}

/**
 * Send chat message to backend with streaming (NO TIMEOUT - data streams continuously)
 * @param {Object} request - { question, session_id, selected_text? }
 * @param {Function} onChunk - Callback for each streamed chunk
 * @returns {Promise<Object>} - { answer, citations, session_id }
 */
export async function sendChatMessage(request, onChunk) {
  try {
    console.log('🌐 [sendChatMessage] Sending request to /api/v1/chat/stream');
    console.log('🌐 [sendChatMessage] Request has selected_text:', !!request.selected_text);
    if (request.selected_text) {
      console.log('🌐 [sendChatMessage] selected_text length:', request.selected_text.length);
      console.log('🌐 [sendChatMessage] section_title:', request.section_title);
    }

    // Use streaming endpoint with NO timeout since data arrives gradually
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ChatAPIError(
        errorData.detail || 'Chat request failed',
        response.status,
        errorData
      );
    }

    // Process streaming response - no timeout since data streams gradually
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let answer = '';
    let citations = [];
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');

        // Keep last incomplete line in buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim().startsWith('data: ')) {
            try {
              const jsonStr = line.trim().slice(6);
              if (!jsonStr) continue;

              const data = JSON.parse(jsonStr);

              if (data.type === 'text_delta') {
                answer += data.delta;
                if (onChunk) onChunk({ type: 'text', delta: data.delta });
              } else if (data.type === 'citation') {
                citations.push(data.ieee);
                if (onChunk) onChunk({ type: 'citation', data: data.ieee });
              } else if (data.type === 'thinking' || data.type === 'retrieving' || data.type === 'selection_mode') {
                // Status messages - log for debugging
                console.log(`📡 [sendChatMessage] Received ${data.type} event: ${data.delta}`);
                if (onChunk) onChunk({ type: 'status', message: data.delta });
              } else if (data.type === 'retrieval') {
                // Retrieval event - log chunk information
                console.log('📡 [sendChatMessage] Vector search returned chunks:', data.chunks?.length || 0);
              } else if (data.type === 'error') {
                console.error('❌ [sendChatMessage] Backend error:', data.message);
                throw new Error(data.message);
              } else if (data.type === 'response_start' || data.type === 'response_end') {
                // Response timing events - log for debugging
                console.log(`📡 [sendChatMessage] ${data.type} event received`);
              }
            } catch (e) {
              console.debug('Could not parse SSE line:', line);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }

    return {
      answer: answer.trim(),
      citations: citations,
      confidence_score: 0.95,
    };
  } catch (error) {
    if (error instanceof ChatAPIError) throw error;
    throw new ChatAPIError(error.message, 0, null);
  }
}

/**
 * Fetch conversation history for a session (no timeout/retry for fast failure)
 * @param {string} sessionId - Session ID
 * @returns {Promise<Object>} - { messages: [...] }
 */
export async function fetchConversationHistory(sessionId) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/chat/history/${sessionId}`,
      {
        method: 'GET',
        credentials: 'include',
      }
    );

    if (!response.ok) {
      throw new ChatAPIError(
        'Failed to load conversation history',
        response.status,
        null
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ChatAPIError) throw error;
    throw new ChatAPIError('Failed to load conversation history', 0, null);
  }
}

/**
 * Create a new chat session (no timeout - uses fetch directly)
 * @returns {Promise<Object>} - { session_id }
 */
export async function createSession() {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/chat/sessions`,
      {
        method: 'POST',
        credentials: 'include',
      }
    );

    if (!response.ok) {
      throw new ChatAPIError(
        'Failed to create session',
        response.status,
        null
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ChatAPIError) throw error;
    throw new ChatAPIError('Failed to create session', 0, null);
  }
}

/**
 * Health check for backend API
 * @returns {Promise<Object>} - { status: 'ok' }
 */
export async function healthCheck() {
  try {
    const response = await fetchWithTimeout(
      `${API_BASE_URL}/api/v1/health`,
      {
        method: 'GET',
        credentials: 'include',
      },
      2000
    );

    if (!response.ok) {
      return { status: 'error' };
    }

    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error.message);
    return { status: 'error' };
  }
}

export { ChatAPIError };
