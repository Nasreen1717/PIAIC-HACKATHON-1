/**
 * usePersonalization Hook
 *
 * Manages content personalization state and API calls.
 *
 * Features:
 * - Fetches article content from DOM via querySelector
 * - POSTs to /api/v1/personalize endpoint with JWT token
 * - Handles response/errors per ADR-004 (graceful degradation)
 * - Manages state: default, loading, personalized, error
 * - Stores original content in ref for reset functionality
 * - Debounces rapid clicks (300ms)
 */

import { useCallback, useRef, useState } from 'react';
import { marked } from 'marked';
import { useAuth } from './useAuth';

// Configure marked for better readability
marked.setOptions({
  breaks: true,
  gfm: true,
  headerIds: true,
  mangle: false,
});

interface UsePersonalizationResult {
  state: 'default' | 'loading' | 'personalized' | 'error';
  error: string | null;
  personalizationLevel: string | null;
  personalizedContent: string | null;
  personalize: (softwareBackground?: string) => Promise<void>;
  resetToOriginal: () => void;
}

export const usePersonalization = (): UsePersonalizationResult => {
  const { user, token } = useAuth();
  const [state, setState] = useState<'default' | 'loading' | 'personalized' | 'error'>('default');
  const [error, setError] = useState<string | null>(null);
  const [personalizationLevel, setPersonalizationLevel] = useState<string | null>(null);
  const [personalizedContent, setPersonalizedContent] = useState<string | null>(null);

  // Store original content and article element
  const originalContentRef = useRef<string>('');
  const articleElementRef = useRef<HTMLElement | null>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isProcessingRef = useRef<boolean>(false);

  const personalize = useCallback(async (softwareBackground?: string) => {
    // Prevent multiple concurrent requests
    if (isProcessingRef.current || state === 'loading') {
      return;
    }

    // Debounce rapid clicks (300ms)
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(async () => {
      try {
        isProcessingRef.current = true;
        setState('loading');
        setError(null);

        // Get article element and content from DOM
        const articleElement = document.querySelector('article');
        if (!articleElement) {
          setState('error');
          setError('No article content found. Please refresh the page.');
          isProcessingRef.current = false;
          return;
        }

        // Store references for reset
        articleElementRef.current = articleElement;
        originalContentRef.current = articleElement.innerHTML;

        // Extract content using innerText to preserve line breaks and structure
        // (unlike textContent which removes all formatting and newlines)
        const articleContent = articleElement.innerText || '';

        if (!articleContent.trim()) {
          setState('error');
          setError('No content found on this page.');
          isProcessingRef.current = false;
          return;
        }

        // Get user profile from context (with fallback defaults)
        if (!user) {
          setState('error');
          setError('Not authenticated. Please sign in again.');
          isProcessingRef.current = false;
          return;
        }

        // Prepare request with defaults if profile incomplete
        const requestBody = {
          content: articleContent,
          software_background: softwareBackground || user.background?.software_background || 'intermediate',
          hardware_background: user.background?.hardware_background || 'none',
          learning_goal: user.background?.learning_goal || 'career',
        };

        // Call backend endpoint
        const apiUrl =
          typeof process !== 'undefined' && process.env?.REACT_APP_API_URL
            ? process.env.REACT_APP_API_URL
            : 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/personalize`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify(requestBody),
        });

        // Handle HTTP errors
        if (!response.ok) {
          const data = await response.json().catch(() => ({}));
          const errorDetail = data.detail || 'Personalization failed';

          switch (response.status) {
            case 401:
              // Unauthorized - redirect to signin
              setState('error');
              setError('Your session expired. Please sign in again.');
              // Trigger redirect after a short delay
              setTimeout(() => {
                window.location.href = '/signin';
              }, 1500);
              isProcessingRef.current = false;
              return;

            case 429:
              // Rate limited
              setState('error');
              setError('Service is busy. Please wait a moment and try again.');
              isProcessingRef.current = false;
              return;

            case 504:
              // Timeout
              setState('error');
              setError('Service took too long to respond. Please try again.');
              isProcessingRef.current = false;
              return;

            default:
              setState('error');
              setError(errorDetail);
              isProcessingRef.current = false;
              return;
          }
        }

        // Parse successful response
        const personalizedData = await response.json();

        // Store and convert personalized content from markdown to HTML
        if (personalizedData.personalized_content) {
          setPersonalizedContent(personalizedData.personalized_content);

          // Update article content with personalized content
          if (articleElementRef.current) {
            try {
              // Convert markdown to HTML using marked
              const htmlContent = marked(personalizedData.personalized_content);

              // Create a temporary element to safely set HTML and apply formatting classes
              const tempDiv = document.createElement('div');
              tempDiv.innerHTML = htmlContent as string;

              // Add CSS classes to elements for better styling
              // Add class to headings
              tempDiv.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach((el) => {
                el.classList.add('personalized-heading');
              });

              // Add class to paragraphs
              tempDiv.querySelectorAll('p').forEach((el) => {
                el.classList.add('personalized-paragraph');
              });

              // Add class to lists
              tempDiv.querySelectorAll('ul, ol').forEach((el) => {
                el.classList.add('personalized-list');
              });

              // Add class to code blocks
              tempDiv.querySelectorAll('pre, code').forEach((el) => {
                el.classList.add('personalized-code');
              });

              // Add class to blockquotes
              tempDiv.querySelectorAll('blockquote').forEach((el) => {
                el.classList.add('personalized-blockquote');
              });

              // Add class to images
              tempDiv.querySelectorAll('img').forEach((el) => {
                el.classList.add('personalized-image');
              });

              // Add class to tables
              tempDiv.querySelectorAll('table').forEach((el) => {
                el.classList.add('personalized-table');
              });

              // Replace article content with styled version
              articleElementRef.current.innerHTML = tempDiv.innerHTML;
            } catch (parseError) {
              console.error('Error converting markdown to HTML:', parseError);
              // Fallback: use raw content if conversion fails
              articleElementRef.current.innerHTML = personalizedData.personalized_content;
            }
          }
        }

        // Update state
        setState('personalized');
        setPersonalizationLevel(personalizedData.personalization_level);
        setError(null);
      } catch (err) {
        // Network or parsing error
        console.error('Personalization error:', err);
        setState('error');

        if (err instanceof TypeError) {
          setError('Network error. Please check your connection and try again.');
        } else {
          setError('An unexpected error occurred. Please try again.');
        }
      } finally {
        isProcessingRef.current = false;
      }
    }, 300);
  }, [user, token, state]);

  const resetToOriginal = useCallback(() => {
    // Restore original content instantly (< 50ms)
    if (articleElementRef.current && originalContentRef.current) {
      articleElementRef.current.innerHTML = originalContentRef.current;
    }

    // Reset state
    setState('default');
    setError(null);
    setPersonalizationLevel(null);
    setPersonalizedContent(null);
    originalContentRef.current = '';
    articleElementRef.current = null;
  }, []);

  return {
    state,
    error,
    personalizationLevel,
    personalizedContent,
    personalize,
    resetToOriginal,
  };
};
