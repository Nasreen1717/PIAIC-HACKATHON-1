import React, { useState } from 'react';
import { useChatContext } from '@site/src/context/ChatContext';
import styles from './styles.module.css';

/**
 * SelectedTextBanner Component
 *
 * Displays the currently selected text in a banner format above chat messages.
 * Allows users to:
 * - View the selected text snippet (expandable)
 * - See the source (chapter/section title)
 * - Clear the selection to revert to vector search
 *
 * **T085**: Selected text display with expand/collapse
 * **T086**: Source attribution
 * **T087**: Clear button with state management
 */
const SelectedTextBanner = () => {
  const { selectedText, selectedContext, dispatch } = useChatContext();
  const [expanded, setExpanded] = useState(false);

  if (!selectedText || !selectedContext) {
    return null;
  }

  const handleClear = () => {
    dispatch({
      type: 'SET_SELECTED_TEXT',
      payload: {
        selected_text: null,
        chapter_path: null,
        section_id: null,
        section_title: null,
        context_before: null,
        context_after: null,
      },
    });
  };

  const displayText = expanded
    ? selectedText
    : selectedText.substring(0, 100) + (selectedText.length > 100 ? '...' : '');

  return (
    <div className={styles.selectedTextBanner}>
      <div className={styles.bannerHeader}>
        <span className={styles.bannerIcon}>📄</span>
        <span className={styles.bannerTitle}>Selected Text Context</span>
        <button
          className={styles.bannerClearButton}
          onClick={handleClear}
          title="Clear selection"
          aria-label="Clear selected text"
        >
          ✕
        </button>
      </div>

      <div className={styles.bannerContent}>
        <p className={styles.selectedTextSnippet}>{displayText}</p>

        {selectedText.length > 100 && (
          <button
            className={styles.bannerToggleButton}
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? "Show less ▲" : "Show more ▼"}
          </button>
        )}

        {selectedContext.section_title && (
          <p className={styles.bannerSource}>
            From: {selectedContext.section_title}
          </p>
        )}
      </div>

      <div className={styles.bannerFooter}>
        <span className={styles.bannerNote}>
          Answers will be based on this selected text
        </span>
      </div>
    </div>
  );
};

export default SelectedTextBanner;
