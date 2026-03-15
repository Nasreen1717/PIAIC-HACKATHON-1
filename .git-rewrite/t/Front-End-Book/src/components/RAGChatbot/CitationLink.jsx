import React, { useState, useMemo } from 'react';
import styles from './styles.module.css';

/**
 * T065: Citation Link Component
 * Displays citations in IEEE format.
 * Clickable to navigate to source section.
 * Hover shows tooltip with source text preview.
 */
export default function CitationLink({ citation }) {
  const [showTooltip, setShowTooltip] = useState(false);

  // Validate and memoize citation data
  const citationData = useMemo(() => {
    if (!citation) return null;
    const chapter = Math.max(1, parseInt(citation.chapter_number) || 1);
    const section = String(citation.section_id || 'selected').trim();
    const title = String(citation.section_title || 'Unknown').trim();
    return { chapter, section, title, url: citation.url };
  }, [citation]);

  if (!citationData) {
    return null;
  }

  // Format: [Chapter X, Section Y: "Title"]
  const ieeeFormat = `[Chapter ${citationData.chapter}, Section ${citationData.section}: "${citationData.title}"]`;

  const handleClick = (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }

    try {
      let url = citationData.url;

      // If no URL from backend, generate it
      if (!url) {
        try {
          const moduleNumber = Math.ceil(citationData.chapter / 3);
          const sectionAnchor = citationData.section.replace(/\./g, '-');
          url = `/docs/module-${moduleNumber}/chapter-${citationData.chapter}#${sectionAnchor}`;
        } catch (genError) {
          console.error('Error generating citation URL:', genError, citationData);
          url = '/docs';
        }
      }

      if (url) {
        window.location.href = url;
      }
    } catch (error) {
      console.error('Error handling citation click:', error, { citationData });
    }
  };

  return (
    <span
      className={styles.citationLink}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyPress={(e) => {
        if (e.key === 'Enter') {
          handleClick(e);
        }
      }}
    >
      {ieeeFormat}
      {showTooltip && citation?.source_text && (
        <span className={styles.tooltip}>
          {citation.source_text.substring(0, 100)}...
        </span>
      )}
    </span>
  );
}
