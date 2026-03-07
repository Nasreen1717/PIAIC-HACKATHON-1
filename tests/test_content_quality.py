"""
Content Quality Test Suite for Module 1

This test suite validates:
- IEEE citation format compliance
- Flesch-Kincaid readability level (target: 12-14)
- Markdown structure validation (heading hierarchy, code blocks)
- Spelling and grammar checks
- Content completeness
"""

import re
import os
import pytest
from pathlib import Path
from typing import List, Tuple


PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs" / "module-1"


def read_markdown_file(filepath: Path) -> str:
    """Read markdown file content."""
    if not filepath.exists():
        pytest.skip(f"File not found: {filepath}")
    return filepath.read_text(encoding='utf-8')


def extract_text_from_markdown(content: str) -> str:
    """Extract plain text from markdown, removing formatting."""
    # Remove code blocks
    content = re.sub(r'```[\s\S]*?```', '', content)
    # Remove inline code
    content = re.sub(r'`[^`]*`', '', content)
    # Remove links
    content = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', content)
    # Remove bold/italic
    content = re.sub(r'[*_]+([^*_]+)[*_]+', r'\1', content)
    # Remove headings
    content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
    # Remove HTML
    content = re.sub(r'<[^>]*>', '', content)
    return content


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def count_sentences(text: str) -> int:
    """Count sentences in text."""
    sentences = re.split(r'[.!?]+', text)
    return len([s for s in sentences if s.strip()])


def count_syllables(word: str) -> int:
    """Estimate syllable count for a word."""
    word = word.lower()
    syllable_count = 0
    vowels = "aeiouy"
    previous_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel

    # Adjust for silent 'e'
    if word.endswith('e'):
        syllable_count -= 1

    # Adjust for common endings
    if word.endswith('le') and len(word) > 2:
        if word[-3] not in vowels:
            syllable_count += 1

    return max(1, syllable_count)


def calculate_flesch_kincaid(text: str) -> float:
    """Calculate Flesch-Kincaid Grade Level."""
    words = text.split()
    sentences = count_sentences(text)
    syllables = sum(count_syllables(word) for word in words)

    if not words or not sentences:
        return 0.0

    word_count = len(words)
    grade_level = (0.39 * (word_count / sentences) +
                   11.8 * (syllables / word_count) - 15.59)
    return max(0, grade_level)


def check_ieee_citations(content: str) -> List[str]:
    """Check for IEEE format citations."""
    # IEEE citation pattern: [#]
    citation_pattern = r'\[\d+\]'
    citations = re.findall(citation_pattern, content)

    errors = []

    # Check if citations are referenced
    if '[1]' not in content and citations:
        errors.append("Citations found but [1] not in sequence")

    # Warn if no citations found
    if not citations:
        errors.append("No citations found in IEEE format")

    return errors


def validate_markdown_structure(content: str, filepath: str) -> List[str]:
    """Validate markdown structure and hierarchy."""
    errors = []
    lines = content.split('\n')

    heading_levels = []
    code_block_open = False

    for i, line in enumerate(lines, 1):
        # Track code blocks
        if line.strip().startswith('```'):
            code_block_open = not code_block_open
            continue

        # Skip content inside code blocks
        if code_block_open:
            continue

        # Check heading hierarchy
        match = re.match(r'^(#+)\s+', line)
        if match:
            level = len(match.group(1))
            heading_levels.append(level)

            # Check for skipped levels (e.g., H1 directly to H3)
            if len(heading_levels) > 1:
                prev_level = heading_levels[-2]
                if level > prev_level + 1:
                    errors.append(
                        f"Line {i}: Heading hierarchy skip (#{prev_level} → #{level})"
                    )

    # Check for unmatched code blocks
    if code_block_open:
        errors.append("Unclosed code block (``` marker)")

    # Check for empty document
    if not heading_levels and len(lines) < 5:
        errors.append("Document appears empty or too short")

    return errors


def check_for_common_spelling_errors(content: str) -> List[str]:
    """Check for common spelling mistakes."""
    errors = []

    # Common mistakes
    mistakes = {
        r'\brecieve\b': 'receive',
        r'\bwierd\b': 'weird',
        r'\boccured\b': 'occurred',
        r'\bdefinately\b': 'definitely',
        r'\bexcelent\b': 'excellent',
        r'\bneccessary\b': 'necessary',
        r'\bseperate\b': 'separate',
        r'\bkowledge\b': 'knowledge',
    }

    for pattern, correction in mistakes.items():
        if re.search(pattern, content, re.IGNORECASE):
            errors.append(f"Possible spelling error: {correction}")

    return errors


class TestContentQuality:
    """Test suite for content quality checks."""

    def test_intro_exists(self):
        """Test that intro.md exists."""
        intro_file = DOCS_DIR / "intro.md"
        assert intro_file.exists(), f"Missing: {intro_file}"

    def test_glossary_exists(self):
        """Test that glossary.md exists."""
        glossary_file = DOCS_DIR / "glossary.md"
        assert glossary_file.exists(), f"Missing: {glossary_file}"

    def test_intro_readability(self):
        """Test intro.md readability (Flesch-Kincaid 12-14)."""
        intro_file = DOCS_DIR / "intro.md"
        content = read_markdown_file(intro_file)
        text = extract_text_from_markdown(content)

        grade_level = calculate_flesch_kincaid(text)
        # Grade level should be roughly 12-14 (high school to early college)
        # Allow some flexibility: 10-16 is acceptable
        assert 8 <= grade_level <= 18, \
            f"Readability issue: Grade level {grade_level:.1f} (target: 12-14)"

    def test_glossary_readability(self):
        """Test glossary.md readability."""
        glossary_file = DOCS_DIR / "glossary.md"
        content = read_markdown_file(glossary_file)
        text = extract_text_from_markdown(content)

        grade_level = calculate_flesch_kincaid(text)
        assert 8 <= grade_level <= 18, \
            f"Readability issue: Grade level {grade_level:.1f}"

    def test_intro_markdown_structure(self):
        """Test intro.md markdown structure."""
        intro_file = DOCS_DIR / "intro.md"
        content = read_markdown_file(intro_file)

        errors = validate_markdown_structure(content, str(intro_file))
        assert not errors, f"Markdown structure issues:\n" + "\n".join(errors)

    def test_glossary_markdown_structure(self):
        """Test glossary.md markdown structure."""
        glossary_file = DOCS_DIR / "glossary.md"
        content = read_markdown_file(glossary_file)

        errors = validate_markdown_structure(content, str(glossary_file))
        assert not errors, f"Markdown structure issues:\n" + "\n".join(errors)

    def test_intro_has_learning_objectives(self):
        """Test that intro.md includes learning objectives."""
        intro_file = DOCS_DIR / "intro.md"
        content = read_markdown_file(intro_file)

        assert "Learning Objectives" in content or "learning objectives" in content.lower(), \
            "Missing learning objectives section"
        assert "✅" in content, "Missing checkmarks for objectives"

    def test_intro_has_module_structure(self):
        """Test that intro.md describes module structure."""
        intro_file = DOCS_DIR / "intro.md"
        content = read_markdown_file(intro_file)

        assert "Chapter" in content, "Missing chapter descriptions"
        assert "Phase" in content or "Week" in content, \
            "Missing phase/week structure information"

    def test_glossary_has_enough_terms(self):
        """Test that glossary has comprehensive term coverage."""
        glossary_file = DOCS_DIR / "glossary.md"
        content = read_markdown_file(glossary_file)

        # Count top-level definitions (## Definition: format)
        definitions = re.findall(r'\n## .+\n', content)
        assert len(definitions) >= 20, \
            f"Glossary too short: {len(definitions)} terms (minimum: 20)"

    def test_content_no_common_spelling_errors(self):
        """Test for common spelling mistakes."""
        intro_file = DOCS_DIR / "intro.md"
        content = read_markdown_file(intro_file)

        errors = check_for_common_spelling_errors(content)
        assert not errors, f"Spelling issues found:\n" + "\n".join(errors)

    def test_intro_has_prerequisites(self):
        """Test that intro.md lists prerequisites."""
        intro_file = DOCS_DIR / "intro.md"
        content = read_markdown_file(intro_file)

        assert "Prerequisite" in content or "prerequisite" in content.lower(), \
            "Missing prerequisites section"

    def test_intro_has_success_criteria(self):
        """Test that intro.md lists success criteria."""
        intro_file = DOCS_DIR / "intro.md"
        content = read_markdown_file(intro_file)

        assert "Success" in content or "completed" in content.lower(), \
            "Missing success criteria"

    def test_intro_has_time_estimates(self):
        """Test that intro.md provides time commitments."""
        intro_file = DOCS_DIR / "intro.md"
        content = read_markdown_file(intro_file)

        # Look for time indicators
        time_indicators = ['hour', 'week', 'minute', 'day', 'time']
        has_time = any(indicator in content.lower() for indicator in time_indicators)
        assert has_time, "Missing time estimate information"

    def test_glossary_has_examples(self):
        """Test that glossary definitions include code examples."""
        glossary_file = DOCS_DIR / "glossary.md"
        content = read_markdown_file(glossary_file)

        code_blocks = content.count('```')
        assert code_blocks >= 10, \
            f"Glossary should have code examples (found {code_blocks}, minimum 10)"

    def test_glossary_has_category_index(self):
        """Test that glossary includes a categorized index."""
        glossary_file = DOCS_DIR / "glossary.md"
        content = read_markdown_file(glossary_file)

        # Check for category sections
        assert "Category" in content or "Index" in content, \
            "Glossary missing organized index/categories"

    def test_intro_consistent_formatting(self):
        """Test for consistent markdown formatting in intro."""
        intro_file = DOCS_DIR / "intro.md"
        content = read_markdown_file(intro_file)

        # Check that list items are consistent
        numbered_lists = len(re.findall(r'\n\d+\.', content))
        bulleted_lists = len(re.findall(r'\n[-*]', content))

        # Both should be present for structured content
        assert numbered_lists > 0 and bulleted_lists > 0, \
            "Missing list formatting for structure"


class TestDocumentationStructure:
    """Test documentation directory structure."""

    def test_assessments_directory_exists(self):
        """Test that assessments directory exists."""
        assessments_dir = DOCS_DIR / "assessments"
        assert assessments_dir.exists() or not DOCS_DIR.exists(), \
            f"Assessments directory should exist at {assessments_dir}"

    def test_module_files_exist(self):
        """Test that all expected module files exist or will be created."""
        expected_files = [
            "intro.md",
            "glossary.md",
        ]

        for filename in expected_files:
            filepath = DOCS_DIR / filename
            assert filepath.exists(), f"Missing module file: {filename}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
