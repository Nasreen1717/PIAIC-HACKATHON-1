/**
 * AnswerWithCitations Component
 *
 * Parses answer text for inline citations and renders them as clickable links.
 * Converts citation patterns like "[Chapter 4, Section 4.3: \"Title\"]"
 * into proper anchor tags with Docusaurus paths.
 *
 * This component intelligently handles citations that appear inline in the answer text
 * by parsing them and converting them to CitationLink components for proper interaction.
 *
 * @param {string} answer - Answer text potentially containing inline citations
 * @returns {JSX.Element} - Parsed answer with clickable citations
 */

import React from 'react';
import CitationLink from './CitationLink';
import styles from './styles.module.css';

const AnswerWithCitations = ({ answer }) => {
  if (!answer) return null;

  // Pattern: [Chapter X, Section Y: "Title"]
  const citationPattern = /\[Chapter\s+(\d+),\s+Section\s+([^:]+):\s+"([^"]+)"\]/g;

  // Split answer by citations and build JSX elements
  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = citationPattern.exec(answer)) !== null) {
    // Add text before citation
    if (match.index > lastIndex) {
      parts.push(answer.substring(lastIndex, match.index));
    }

    // Add citation as a link
    const citationData = {
      chapter_number: parseInt(match[1]),
      section_id: match[2].trim(),
      section_title: match[3].trim(),
    };

    parts.push(
      <CitationLinkInline
        key={`citation-${match.index}`}
        citation={citationData}
      />
    );

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text after last citation
  if (lastIndex < answer.length) {
    parts.push(answer.substring(lastIndex));
  }

  return <div className={styles.answerContent}>{parts}</div>;
};

/**
 * CitationLinkInline Component
 *
 * Inline citation link that appears within answer text.
 * Different from CitationLink which appears in a separate citations section.
 *
 * @param {Object} citation - Citation data (chapter_number, section_id, section_title)
 * @returns {JSX.Element} - Clickable inline citation
 */
const CitationLinkInline = ({ citation }) => {
  // Validate citation data
  if (!citation || !citation.chapter_number || !citation.section_id) {
    return null;
  }

  const handleClick = (e) => {
    e.preventDefault();

    try {
      // Generate Docusaurus URL
      // Route format: /docs/module-X/chapter-Y#section-id
      const chapterNum = citation?.chapter_number || 1;
      const sectionIdRaw = citation?.section_id || 'selected';
      const moduleNumber = Math.ceil(chapterNum / 3);
      const sectionId = String(sectionIdRaw);
      const sectionAnchor = (sectionId || 'selected').replace(/\./g, '-');
      const url = `/docs/module-${moduleNumber}/chapter-${chapterNum}#${sectionAnchor}`;

      // Navigate using window.location for full page load
      // Or use Link component if using Docusaurus routing
      if (url) {
        window.location.href = url;
      }
    } catch (error) {
      console.error('Error navigating to citation:', error, { citation });
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick(e);
    }
  };

  const citationText = `[Chapter ${citation?.chapter_number || '?'}, Section ${citation?.section_id || '?'}: "${citation?.section_title || 'Unknown'}"]`;

  return (
    <a
      href="#"
      className={styles.inlineCitation}
      onClick={handleClick}
      onKeyPress={handleKeyPress}
      title={`Navigate to ${citation.section_title}`}
      role="link"
      tabIndex={0}
    >
      {citationText}
    </a>
  );
};

export default AnswerWithCitations;
