/**
 * Configuration loader for React components
 * Works with both local backend and Vercel serverless functions
 */

// Determine API base URL
function getApiBaseUrl() {
  // Check if we're in browser
  const isBrowser = typeof window !== 'undefined';

  if (isBrowser) {
    // In browser, check location
    const hostname = window.location.hostname;
    const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1';

    if (isLocalhost) {
      // Local development: use backend on port 8000
      const url = 'http://localhost:8000';
      console.log('[Config] Local development mode - using backend:', url);
      return url;
    } else {
      // Production/Vercel: use relative /api
      console.log('[Config] Production mode - using relative /api path');
      return '/api';
    }
  }

  // Server-side: default to relative path
  return '/api';
}

function getOpenAiKey() {
  // This will be available if REACT_APP_OPENAI_API_KEY was set during build
  if (typeof process !== 'undefined' && process.env?.REACT_APP_OPENAI_API_KEY) {
    return process.env.REACT_APP_OPENAI_API_KEY;
  }
  return '';
}

export const API_BASE_URL = getApiBaseUrl();
export const OPENAI_API_KEY = getOpenAiKey();

if (typeof window !== 'undefined') {
  console.log('[Config] ✅ Initialized with:', {
    API_BASE_URL,
    hostname: window.location.hostname,
    protocol: window.location.protocol,
    hasOpenAiKey: !!OPENAI_API_KEY,
  });
}
