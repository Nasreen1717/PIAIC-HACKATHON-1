"""
Explicit mapping of chapter file paths to Docusaurus URLs.

This file provides a single source of truth for citation URLs.
Every URL has been verified against the actual Docusaurus file structure.

Format: {chapter_number: (section_id, title, docusaurus_url_path, file_path)}
"""

# Complete mapping of all chapters and reference files
CHAPTER_URL_MAPPING = {
    # Module 1: ROS 2 Fundamentals
    1: {
        "file": "docs/module-1/chapter-1.md",
        "url_base": "/docs/module-1/chapter-1",
        "module": 1,
        "title": "Chapter 1: Introduction to ROS 2"
    },
    2: {
        "file": "docs/module-1/chapter-2.md",
        "url_base": "/docs/module-1/chapter-2",
        "module": 1,
        "title": "Chapter 2: ROS 2 Communication Patterns"
    },
    3: {
        "file": "docs/module-1/chapter-3.md",
        "url_base": "/docs/module-1/chapter-3",
        "module": 1,
        "title": "Chapter 3: Robot Description with URDF"
    },

    # Module 2: Digital Twin
    4: {
        "file": "docs/module-2/chapter-4.md",
        "url_base": "/docs/module-2/chapter-4",
        "module": 2,
        "title": "Chapter 4: Physics Simulation with Gazebo"
    },
    5: {
        "file": "docs/module-2/chapter-5.md",
        "url_base": "/docs/module-2/chapter-5",
        "module": 2,
        "title": "Chapter 5: High-Fidelity Rendering with Unity"
    },
    6: {
        "file": "docs/module-2/chapter-6.md",
        "url_base": "/docs/module-2/chapter-6",
        "module": 2,
        "title": "Chapter 6: Sensor Simulation and Integration"
    },

    # Module 3: Isaac Sim & Advanced Simulation
    7: {
        "file": "docs/module-3/chapter-7-isaac-sim.mdx",
        "url_base": "/docs/module-3/chapter-7-isaac-sim",
        "module": 3,
        "title": "Chapter 7: Isaac Sim Advanced Simulation"
    },
    8: {
        "file": "docs/module-3/chapter-8-isaac-ros.mdx",
        "url_base": "/docs/module-3/chapter-8-isaac-ros",
        "module": 3,
        "title": "Chapter 8: Isaac ROS Integration"
    },
    9: {
        "file": "docs/module-3/chapter-9-nav2-bipedal.mdx",
        "url_base": "/docs/module-3/chapter-9-nav2-bipedal",
        "module": 3,
        "title": "Chapter 9: Nav2 and Bipedal Locomotion"
    },

    # Module 4: Vision-Language Models & Voice
    10: {
        "file": "docs/module-4/chapter-10-voice-to-action.mdx",
        "url_base": "/docs/module-4/chapter-10-voice-to-action",
        "module": 4,
        "title": "Chapter 10: Voice-to-Action Systems"
    },
    11: {
        "file": "docs/module-4/chapter-11-cognitive-planning.mdx",
        "url_base": "/docs/module-4/chapter-11-cognitive-planning",
        "module": 4,
        "title": "Chapter 11: Cognitive Planning with VLA"
    },
    12: {
        "file": "docs/module-4/chapter-12-capstone-humanoid.mdx",
        "url_base": "/docs/module-4/chapter-12-capstone-humanoid",
        "module": 4,
        "title": "Chapter 12: Humanoid Capstone Project"
    },
}

# Reference files (chapter_number = 0)
REFERENCE_FILES = {
    1: {
        "file": "docs/module-1/intro.md",
        "url_base": "/docs/module-1/intro",
        "module": 1,
        "type": "intro"
    },
    2: {
        "file": "docs/module-2/intro.md",
        "url_base": "/docs/module-2/intro",
        "module": 2,
        "type": "intro"
    },
    3: {
        "file": "docs/module-3/intro.md",
        "url_base": "/docs/module-3/intro",
        "module": 3,
        "type": "intro"
    },
    4: {
        "file": "docs/module-4/intro.md",
        "url_base": "/docs/module-4/intro",
        "module": 4,
        "type": "intro"
    },
}


def get_docusaurus_url(chapter_number: int, section_id: str) -> str:
    """
    Get the correct Docusaurus URL for a citation.

    Args:
        chapter_number: Chapter number (1-12) or 0 for reference files
        section_id: Section identifier (e.g., "4.3" or "2.2")

    Returns:
        Full Docusaurus URL path (e.g., "/docs/module-2/chapter-4#4-3")

    Raises:
        ValueError: If chapter_number is invalid
    """
    if chapter_number < 0 or chapter_number > 12:
        raise ValueError(f"Invalid chapter_number: {chapter_number}")

    # Normalize section_id for anchor (replace dots with hyphens)
    anchor = str(section_id).replace(".", "-")

    if chapter_number == 0:
        # Reference file (intro, glossary, etc.)
        # Extract module from section_id
        try:
            module_num = int(str(section_id).split(".")[0])
        except (ValueError, IndexError):
            module_num = 1

        if module_num not in REFERENCE_FILES:
            raise ValueError(f"Invalid module_number: {module_num}")

        ref_file = REFERENCE_FILES[module_num]
        return f"{ref_file['url_base']}#{anchor}"

    else:
        # Regular chapter file
        if chapter_number not in CHAPTER_URL_MAPPING:
            raise ValueError(f"Chapter {chapter_number} not found in mapping")

        chapter_info = CHAPTER_URL_MAPPING[chapter_number]
        return f"{chapter_info['url_base']}#{anchor}"


def validate_url(url: str) -> bool:
    """
    Validate that a URL follows the expected Docusaurus format.

    Args:
        url: URL to validate

    Returns:
        True if URL is valid format, False otherwise
    """
    # Check format: /docs/module-X/chapter-Y#section-id or /docs/module-X/intro#section-id
    import re

    pattern = r"^/docs/module-\d+/(chapter-[\w-]+|intro)#[\w-]+$"
    return bool(re.match(pattern, url))


def get_all_chapters() -> dict:
    """Get all chapter mappings."""
    return CHAPTER_URL_MAPPING


def get_all_references() -> dict:
    """Get all reference file mappings."""
    return REFERENCE_FILES


if __name__ == "__main__":
    # Test all URLs
    print("Validating all chapter URLs...")
    for chapter, info in CHAPTER_URL_MAPPING.items():
        url = get_docusaurus_url(chapter, f"{chapter}.1")
        is_valid = validate_url(url)
        status = "✓" if is_valid else "✗"
        print(f"{status} Chapter {chapter}: {url}")

    print("\nValidating all reference URLs...")
    for module, info in REFERENCE_FILES.items():
        url = get_docusaurus_url(0, f"{module}.1")
        is_valid = validate_url(url)
        status = "✓" if is_valid else "✗"
        print(f"{status} Module {module} intro: {url}")
