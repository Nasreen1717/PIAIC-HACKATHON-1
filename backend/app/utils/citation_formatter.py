"""
Citation formatting utilities for IEEE-style citations.

Converts chunk metadata to properly formatted citations.
Uses explicit URL mapping to ensure correctness.
"""

import re
from typing import Dict, Any, List
from app.utils.citation_url_mapping import get_docusaurus_url, validate_url


class CitationFormatter:
    """Handles IEEE citation formatting."""

    @staticmethod
    def format_ieee_citation(chapter_number: int, section_id: str, section_title: str) -> str:
        """
        Format a citation in IEEE style.

        Args:
            chapter_number: Chapter number (e.g., 2).
            section_id: Section identifier (e.g., "2.1", "2.1.3").
            section_title: Section title.

        Returns:
            IEEE-formatted citation string.

        Example:
            "[Chapter 2, Section 2.1: \"Locomotion Basics\"]"
        """
        return f'[Chapter {chapter_number}, Section {section_id}: "{section_title}"]'

    @staticmethod
    def format_multiple_citations(citations: List[Dict[str, Any]]) -> str:
        """
        Format multiple citations for display.

        Args:
            citations: List of citation dictionaries.

        Returns:
            Formatted citations string suitable for display.
        """
        if not citations:
            return ""

        formatted = []
        for citation in citations:
            fmt = CitationFormatter.format_ieee_citation(
                citation.get("chapter_number", 0),
                citation.get("section_id", ""),
                citation.get("section_title", ""),
            )
            formatted.append(fmt)

        return ", ".join(formatted)

    @staticmethod
    def extract_citation_components(chunk_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract citation components from chunk metadata.

        Args:
            chunk_payload: Chunk metadata from Qdrant.

        Returns:
            Dictionary with chapter_number, section_id, section_title.
        """
        return {
            "chapter_number": chunk_payload.get("chapter_number"),
            "section_id": chunk_payload.get("section_id"),
            "section_title": chunk_payload.get("section_title"),
        }

    @staticmethod
    def validate_citation(chapter: int, section_id: str, section_title: str) -> bool:
        """
        Validate citation has required fields.

        Args:
            chapter: Chapter number.
            section_id: Section identifier.
            section_title: Section title.

        Returns:
            True if all components are present and valid.
        """
        return bool(
            isinstance(chapter, int)
            and chapter > 0
            and section_id
            and isinstance(section_id, str)
            and section_title
            and isinstance(section_title, str)
        )

    @staticmethod
    def generate_docusaurus_url(chapter_number: int, section_id: str) -> str:
        """
        Generate Docusaurus documentation URL from chapter and section.

        Uses explicit URL mapping to ensure correctness.
        Every URL is verified against actual Docusaurus file structure.

        Args:
            chapter_number: Chapter number (1-12, or 0 for intro/reference files).
            section_id: Section identifier (e.g., "4.3", "selected", or "1" for intro).

        Returns:
            URL path for Docusaurus, e.g., "/docs/module-2/chapter-4#4-3"
            For intro files: "/docs/module-2/intro#section-id"

        Raises:
            ValueError: If chapter_number is invalid

        Example:
            >>> CitationFormatter.generate_docusaurus_url(4, "4.3")
            "/docs/module-2/chapter-4#4-3"
            >>> CitationFormatter.generate_docusaurus_url(0, "2.1")
            "/docs/module-2/intro#2-1"
        """
        try:
            # Use explicit mapping - guaranteed to be correct
            url = get_docusaurus_url(chapter_number, section_id)

            # Validate URL format
            if not validate_url(url):
                raise ValueError(f"Generated URL failed validation: {url}")

            return url

        except ValueError as e:
            # Fallback for edge cases (shouldn't happen with valid data)
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Citation URL generation failed: {str(e)}, chapter={chapter_number}, section={section_id}")

            # Return a safe fallback URL that will at least navigate to docs
            anchor = str(section_id).replace(".", "-")
            try:
                module_number = int(str(section_id).split(".")[0]) if "." in str(section_id) else 1
            except (ValueError, IndexError):
                module_number = 1

            if chapter_number == 0:
                return f"/docs/module-{module_number}/intro#{anchor}"
            else:
                # Try to use the mapping for chapter-based URL
                if chapter_number in get_docusaurus_url.__globals__.get('CHAPTER_URL_MAPPING', {}):
                    mapping = get_docusaurus_url.__globals__['CHAPTER_URL_MAPPING'][chapter_number]
                    return f"{mapping['url_base']}#{anchor}"
                else:
                    # Last resort: construct URL from chapter number
                    module = (chapter_number - 1) // 3 + 1
                    return f"/docs/module-{module}/chapter-{chapter_number}#{anchor}"

    @staticmethod
    def clean_answer_text(answer_text: str) -> str:
        """
        Remove inline citations from answer text.

        Removes text matching pattern: [Chapter X, Section Y: "Title"]
        This cleans the answer so citations are displayed separately as links.

        Args:
            answer_text: Answer text potentially containing inline citations.

        Returns:
            Answer text with inline citations removed.

        Example:
            >>> text = 'Bipedal locomotion is... [Chapter 2, Section 2.1: "Locomotion"]'
            >>> CitationFormatter.clean_answer_text(text)
            'Bipedal locomotion is...'
        """
        # Pattern: [Chapter X, Section Y: "Title"]
        pattern = r"\s*\[Chapter\s+\d+,\s+Section\s+[^:]+:\s+\"[^\"]+\"\]\s*"
        cleaned = re.sub(pattern, " ", answer_text)

        # Clean up multiple spaces
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned

    @staticmethod
    def extract_inline_citations(answer_text: str) -> List[Dict[str, str]]:
        """
        Extract inline citations from answer text.

        Finds all text matching pattern: [Chapter X, Section Y: "Title"]
        Useful for frontend parsing and linkification.

        Args:
            answer_text: Answer text potentially containing inline citations.

        Returns:
            List of citation dicts with chapter_number, section_id, section_title.

        Example:
            >>> text = 'Answer with [Chapter 2, Section 2.1: "Basics"] citation'
            >>> CitationFormatter.extract_inline_citations(text)
            [{'chapter_number': 2, 'section_id': '2.1', 'section_title': 'Basics'}]
        """
        citations = []

        # Pattern: [Chapter X, Section Y: "Title"]
        pattern = r"\[Chapter\s+(\d+),\s+Section\s+([^:]+):\s+\"([^\"]+)\"\]"
        matches = re.findall(pattern, answer_text)

        for chapter, section, title in matches:
            citations.append({
                "chapter_number": int(chapter),
                "section_id": section.strip(),
                "section_title": title.strip(),
            })

        return citations


# Global instance for convenience
citation_formatter = CitationFormatter()
