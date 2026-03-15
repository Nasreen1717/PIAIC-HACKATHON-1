/**
 * TextSelectionHandler Component
 *
 * Detects text selection on the page and provides an interface to ask questions
 * about the selected text. Extracts chapter and section context from the DOM.
 *
 * **T038**: Creates text selection capture functionality with DOM traversal
 * to extract chapter/section metadata from Docusaurus content.
 *
 * Features:
 * - Detects mouse selection events
 * - Extracts chapter/section from DOM context
 * - Shows floating action button for selected text
 * - Passes selection context to ChatInterface
 *
 * @returns {null} - Returns null as this is a handler component (uses context)
 */

import React, { useState, useEffect } from 'react';
import { useChatContext } from '../../context/ChatContext';
import styles from './styles.module.css';

const TextSelectionHandler = () => {
  let chatContext;
  try {
    chatContext = useChatContext();
  } catch (error) {
    console.warn('TextSelectionHandler: Not inside ChatProvider, skipping', error.message);
    return null;
  }

  const { dispatch } = chatContext;
  const [selectedText, setSelectedText] = useState('');
  const [selectionContext, setSelectionContext] = useState(null);
  const [showSelectionButton, setShowSelectionButton] = useState(false);
  const [buttonPosition, setButtonPosition] = useState({ x: 0, y: 0 });

  /**
   * Extract chapter information from DOM traversal.
   * Looks for common Docusaurus and documentation patterns.
   *
   * @returns {Object} Chapter metadata with number, title, path
   */
  const extractChapterContext = () => {
    let chapterNumber = 0;
    let chapterTitle = '';
    let sectionId = '';
    let sectionTitle = '';
    let moduleNum = 0;

    // Try to find chapter from breadcrumb or page title
    const breadcrumb = document.querySelector('.breadcrumbs__item, .DocItem_title');
    if (breadcrumb) {
      chapterTitle = breadcrumb.textContent?.trim() || '';
    }

    // Try to find h1 (page title)
    const h1 = document.querySelector('h1');
    if (h1 && !chapterTitle) {
      chapterTitle = h1.textContent?.trim() || '';
    }

    // Try to find module and chapter from sidebar
    const sidebar = document.querySelector('.sidebar-content, nav');
    if (sidebar) {
      const activeLink = sidebar.querySelector('.active, [aria-current="page"]');
      if (activeLink) {
        const text = activeLink.textContent?.trim() || '';
        // Parse "Module X - Chapter Y: Title" or "Chapter Y: Title"
        const moduleMatch = text.match(/Module (\d+)/i);
        const chapterMatch = text.match(/Chapter (\d+)/i);

        if (moduleMatch) moduleNum = parseInt(moduleMatch[1]);
        if (chapterMatch) chapterNumber = parseInt(chapterMatch[1]);
      }
    }

    // Try to find section ID from the closest heading
    const selection = window.getSelection();
    if (selection && selection.anchorNode) {
      let element = selection.anchorNode.parentElement;

      // Traverse up to find heading with ID
      while (element && !sectionId) {
        if (element.id) {
          sectionId = element.id;
        }
        // Look for heading tags
        if (/^H[2-6]$/.test(element.tagName)) {
          sectionTitle = element.textContent?.trim() || '';
          if (!sectionId) {
            // Generate ID from heading text if not found
            sectionId = sectionTitle
              .toLowerCase()
              .replace(/[^\w\s-]/g, '')
              .replace(/\s+/g, '-')
              .substring(0, 50);
          }
          break;
        }
        element = element.parentElement;
      }
    }

    // Estimate chapter path from URL if available
    const currentPath = window.location.pathname;
    const pathMatch = currentPath.match(/module[\/-](\d+).*chapter[\/-](\d+)/i) ||
                      currentPath.match(/chapter[\/-](\d+)/i);

    if (pathMatch) {
      if (pathMatch.length > 2) {
        moduleNum = parseInt(pathMatch[1]);
        chapterNumber = parseInt(pathMatch[2]);
      } else if (pathMatch.length > 1) {
        chapterNumber = parseInt(pathMatch[1]);
      }
    }

    return {
      chapter_number: chapterNumber || 0,
      chapter_title: chapterTitle,
      chapter_path: currentPath,
      module_number: moduleNum,
      section_id: sectionId || 'selected',
      section_title: sectionTitle || 'Selected Text',
    };
  }

  /**
   * Extract context before and after the selection.
   * Provides surrounding text for better LLM understanding.
   *
   * @returns {Object} Context with before/after text
   */
  const extractContextAround = () => {
    const selection = window.getSelection();
    if (!selection || selection.toString().length === 0) {
      return { context_before: '', context_after: '' };
    }

    let contextBefore = '';
    let contextAfter = '';

    try {
      const range = selection.getRangeAt(0);

      // Get context before selection
      const beforeRange = range.cloneRange();
      beforeRange.collapse(true);
      beforeRange.setStart(beforeRange.commonAncestorContainer, 0);
      const beforeText = beforeRange.toString();
      contextBefore = beforeText.slice(-200); // Last 200 chars

      // Get context after selection
      const afterRange = range.cloneRange();
      afterRange.collapse(false);
      const endContainer = afterRange.commonAncestorContainer;
      afterRange.setEnd(endContainer, endContainer.length || 0);
      const afterText = afterRange.toString();
      contextAfter = afterText.slice(0, 200); // First 200 chars
    } catch (e) {
      console.warn('Could not extract surrounding context:', e);
    }

    return {
      context_before: contextBefore,
      context_after: contextAfter,
    };
  };

  /**
   * Handle text selection event.
   * Shows action button when text is selected.
   */
  const handleTextSelection = () => {
    const selection = window.getSelection();
    const selectedContent = selection.toString().trim();

    if (selectedContent.length > 0) {
      setSelectedText(selectedContent);

      // Get bounding box for button positioning
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();

      setButtonPosition({
        x: rect.right + 10,
        y: rect.top,
      });

      // Extract context for later use
      const chapterContext = extractChapterContext();
      const surroundingContext = extractContextAround();

      setSelectionContext({
        ...chapterContext,
        ...surroundingContext,
      });

      setShowSelectionButton(true);
    } else {
      setShowSelectionButton(false);
      setSelectedText('');
    }
  };

  /**
   * Handle click on "Ask about selection" button.
   * Passes selected text and context to ChatInterface.
   * **T077**: Keep selection visible while chatbot is open
   * **T078**: Add comprehensive logging for debugging
   */
  const handleAskAboutSelection = (e) => {
    console.log('🔍 [TextSelectionHandler] handleAskAboutSelection called');

    if (e) {
      e.preventDefault();
      e.stopPropagation();
      console.log('🔍 [TextSelectionHandler] Event prevented and stopped');
    }

    console.log('🔍 [TextSelectionHandler] selectedText:', selectedText?.substring(0, 50));
    console.log('🔍 [TextSelectionHandler] selectionContext:', selectionContext);

    if (selectedText && selectionContext) {
      console.log('✅ [TextSelectionHandler] Both selectedText and context exist, dispatching...');

      const payload = {
        selected_text: selectedText,
        chapter_path: selectionContext.chapter_path,
        section_id: selectionContext.section_id,
        section_title: selectionContext.section_title,
        context_before: selectionContext.context_before,
        context_after: selectionContext.context_after,
        chapter_number: selectionContext.chapter_number,
      };

      // Dispatch action to set selected text in chat context
      console.log('📤 [TextSelectionHandler] Dispatching SET_SELECTED_TEXT...');
      dispatch({
        type: 'SET_SELECTED_TEXT',
        payload: payload,
      });
      console.log('✅ [TextSelectionHandler] SET_SELECTED_TEXT dispatched');

      // Show chat interface with focus on input
      console.log('📤 [TextSelectionHandler] Dispatching SET_IS_OPEN...');
      dispatch({ type: 'SET_IS_OPEN', payload: true });
      console.log('✅ [TextSelectionHandler] SET_IS_OPEN dispatched');

      // DO NOT clear selection UI - keep it visible so user can see what they're discussing
      // Selection UI will be cleared when user makes a new selection or page is refreshed
    } else {
      console.log('❌ [TextSelectionHandler] Missing selectedText or selectionContext!');
      console.log('  selectedText exists?', !!selectedText);
      console.log('  selectionContext exists?', !!selectionContext);
    }
  };

  /**
   * Set up selection listeners on mount.
   */
  useEffect(() => {
    document.addEventListener('mouseup', handleTextSelection);
    document.addEventListener('touchend', handleTextSelection);

    return () => {
      document.removeEventListener('mouseup', handleTextSelection);
      document.removeEventListener('touchend', handleTextSelection);
    };
  }, []);

  // Render floating button when text is selected
  if (!showSelectionButton) {
    return null;
  }

  return (
    <div
      className={styles.textSelectionButton}
      style={{
        position: 'fixed',
        top: `${buttonPosition.y}px`,
        left: `${buttonPosition.x}px`,
        zIndex: 999, // Below chat but above content
      }}
    >
      <button
        onClick={(e) => {
          console.log('🖱️ [TextSelectionHandler] Button clicked!');
          handleAskAboutSelection(e);
        }}
        title="Ask about selected text"
        className={styles.selectionActionButton}
        aria-label="Ask chatbot about selected text"
      >
        <span className={styles.selectionButtonIcon}>💬</span>
        <span className={styles.selectionButtonText}>Ask about this</span>
      </button>
      <div className={styles.selectionPreview}>
        <p className={styles.previewTitle}>Selected Text</p>
        <p className={styles.previewContent}>{selectedText.substring(0, 100)}{selectedText.length > 100 ? '...' : ''}</p>
        {selectionContext && selectionContext.section_title && (
          <p className={styles.previewSource}>
            From: {selectionContext.chapter_title ? `${selectionContext.chapter_title} / ` : ''}
            {selectionContext.section_title}
          </p>
        )}
      </div>
    </div>
  );
};

export default TextSelectionHandler;
