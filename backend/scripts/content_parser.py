"""
Markdown/MDX parser for extracting textbook content.

Parses chapters, sections, and content from the Physical AI textbook files.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import frontmatter


class ContentParser:
    """Parses markdown/MDX files to extract structured content."""

    def __init__(self, base_path: str = "Front-End-Book/docs"):
        """
        Initialize parser with base path to textbook.

        Args:
            base_path: Root path to textbook documentation.
        """
        self.base_path = Path(base_path)

    def parse_chapter(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a single chapter file.

        Args:
            file_path: Path to markdown/MDX file.

        Returns:
            Structured chapter data with metadata and sections.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)

            # Extract metadata
            metadata = post.metadata
            content = post.content

            # Parse module and chapter info from path
            relative_path = file_path.relative_to(self.base_path)
            parts = relative_path.parts

            # Expected structure: module-X/chapter-Y-name.md or module-X/intro.md
            module_match = re.search(r"module-(\d+)", parts[0]) if parts else None
            chapter_match = re.search(r"chapter-(\d+)", file_path.name)

            module_number = int(module_match.group(1)) if module_match else 0
            chapter_number = int(chapter_match.group(1)) if chapter_match else 0

            # For reference files (intro, README, glossary), assign chapter_number = 0
            # but store module_number for context
            if file_path.name in ["intro.md", "README.md", "glossary.md"]:
                chapter_number = 0

            # Extract sections
            sections = self._extract_sections(content, chapter_number, module_number)

            return {
                "file_path": str(file_path),
                "module_number": module_number,
                "chapter_number": chapter_number,
                "title": metadata.get("title", file_path.stem),
                "metadata": metadata,
                "sections": sections,
                "raw_content": content,
            }

        except Exception as e:
            print(f"❌ Error parsing {file_path}: {str(e)}")
            return None

    def _extract_sections(self, content: str, chapter_number: int, module_number: int = 0) -> List[Dict[str, Any]]:
        """
        Extract sections from chapter content.

        Args:
            content: Raw markdown content.
            chapter_number: Chapter number for section IDs (0 for reference files).
            module_number: Module number (used when chapter_number=0 for reference files).

        Returns:
            List of sections with content and metadata.
        """
        sections = []
        section_counter = 1

        # Split by heading level 2 or 3 (## Section Title or ### Subsection)
        pattern = r"^#{2,3} (.+?)$"
        matches = list(re.finditer(pattern, content, re.MULTILINE))

        for i, match in enumerate(matches):
            section_title = match.group(1).strip()
            section_start = match.end()

            # Find end of section (next ## or ### or end of content)
            if i < len(matches) - 1:
                section_end = matches[i + 1].start()
            else:
                section_end = len(content)

            section_content = content[section_start:section_end].strip()

            # Skip empty sections
            if not section_content:
                continue

            # Generate section_id: use module.counter for reference files (chapter_number=0)
            # Use chapter.counter for regular chapters
            if chapter_number == 0 and module_number > 0:
                section_id = f"{module_number}.{section_counter}"
            else:
                section_id = f"{chapter_number}.{section_counter}"

            sections.append({
                "section_id": section_id,
                "title": section_title,
                "content": section_content,
                "chapter_number": chapter_number,
                "order": section_counter,
            })

            section_counter += 1

        return sections

    def parse_all_chapters(self) -> List[Dict[str, Any]]:
        """
        Parse all chapter files in the textbook.

        Returns:
            List of parsed chapter data.
        """
        chapters = []

        # Find all .md and .mdx files (chapters + intro/reference files)
        # Only include files from module-X directories (direct children, not subdirectories)
        include_names = ["chapter-", "intro.md", "README.md", "glossary.md"]
        for file_path in self.base_path.rglob("*"):
            if file_path.suffix in [".md", ".mdx"]:
                # Check if file is in a module-X subdirectory
                relative_path = file_path.relative_to(self.base_path)
                parts = relative_path.parts

                # Ensure file is under a module-X directory (not root level)
                # AND is a direct child of module-X (not in exercises/, assessments/, etc.)
                if len(parts) == 2 and parts[0].startswith("module-"):
                    # Include chapter files and reference files (intro, README, glossary)
                    if any(file_path.name.startswith(prefix) if prefix.endswith("-") else file_path.name == prefix for prefix in include_names):
                        chapter_data = self.parse_chapter(file_path)
                        if chapter_data:
                            chapters.append(chapter_data)

        # Sort by module and chapter number (intro=0, README=0.5, glossary=0.9 per module)
        def sort_key(ch):
            module = ch["module_number"]
            name = Path(ch["file_path"]).name
            if name == "intro.md":
                chapter = 0  # First
            elif name == "README.md":
                chapter = 0.5  # Before chapters
            elif name == "glossary.md":
                chapter = 999  # Last
            else:
                chapter = ch["chapter_number"]
            return (module, chapter)

        chapters.sort(key=sort_key)

        return chapters


def parse_textbook(base_path: str = "Front-End-Book/docs") -> List[Dict[str, Any]]:
    """
    Parse entire textbook into structured format.

    Args:
        base_path: Root path to textbook.

    Returns:
        List of chapters with sections.
    """
    parser = ContentParser(base_path)
    chapters = parser.parse_all_chapters()

    print(f"✅ Parsed {len(chapters)} chapters from textbook")

    return chapters


if __name__ == "__main__":
    # Test parsing
    chapters = parse_textbook()
    for chapter in chapters[:1]:  # Print first chapter as example
        print(f"\nChapter {chapter['chapter_number']}: {chapter['title']}")
        print(f"Sections: {len(chapter['sections'])}")
        for section in chapter['sections'][:2]:
            print(f"  - {section['section_id']}: {section['title']}")
