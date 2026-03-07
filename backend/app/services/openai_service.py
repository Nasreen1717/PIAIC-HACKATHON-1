"""
OpenAI integration service for content personalization.

Handles prompt generation and OpenAI API calls for content transformation.
"""

import asyncio
import logging
import re
import time
from typing import Any, Dict, Literal, Tuple

from openai import AsyncOpenAI, RateLimitError

from app.core.config import settings

logger = logging.getLogger(__name__)


def clean_markdown_response(content: str) -> str:
    """
    Clean markdown code fence markers from OpenAI response.

    OpenAI sometimes wraps responses in ```markdown code blocks.
    This function removes those markers while preserving the actual content.

    Args:
        content: Raw response from OpenAI

    Returns:
        Cleaned content without markdown code fence markers
    """
    # Remove markdown code fence markers (```markdown ... ```)
    cleaned = re.sub(r'^```(?:markdown)?\s*\n', '', content)
    cleaned = re.sub(r'\n```\s*$', '', cleaned)
    return cleaned.strip()

# Initialize async OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_personalization_prompt(
    content: str,
    level: Literal["beginner", "intermediate", "advanced"],
    hardware_background: str,
    learning_goal: str,
) -> Tuple[str, str]:
    """
    Generate OpenAI system and user prompts for content personalization.

    Args:
        content: Article content to personalize
        level: Personalization level (beginner/intermediate/advanced)
        hardware_background: User's hardware context (none/basic/advanced)
        learning_goal: User's learning goal (career/hobby/research)

    Returns:
        Tuple of (system_prompt, user_prompt)
    """

    # System prompts for each level
    system_prompts = {
        "beginner": """You are a professional educator specializing in making complex technical content accessible to beginners.

Your task is to transform technical content for beginners while maintaining 100% accuracy.

PRESERVE EXACTLY - DO NOT MODIFY:
- All IEEE-formatted citations (format: [N], [Author Year])
- All code examples (line-by-line, syntax, logic, version numbers)
- All technical facts, APIs, version numbers, and safety protocols
- All learning objectives and key concepts

TRANSFORM AS FOLLOWS:
- Reading level: Target Flesch-Kincaid grade 12-14
- Language: Use simple, everyday terms; explain all technical jargon
- Structure: Use numbered lists and step-by-step approaches
- Add: 💡 Tip boxes for key insights
- Add: ⚠️ Common Mistake sections to prevent pitfalls
- Add: Glossary links for technical terms
- Add: Real-world analogies to familiar concepts
- Code comments: Detailed, explain logic and purpose
- Hardware: Emphasize cloud and simulation options (no GPU required)
- Tone: Encouraging, supportive, patient
- Math: Explain formulas before using them
- Length: May be longer due to explanations (this is fine)

Remember: Your goal is comprehension. Beginners should understand concepts, not just read them.""",
        "intermediate": """You are a professional technical writer specializing in clear, accurate technical documentation.

Your task is to maintain balanced technical content for intermediate learners.

PRESERVE EXACTLY - DO NOT MODIFY:
- All IEEE-formatted citations
- All code examples (line-by-line, syntax, logic, version numbers)
- All technical facts, APIs, version numbers, and safety protocols
- All learning objectives

TRANSFORM AS FOLLOWS:
- Language: Use balanced technical terminology with brief explanations
- Structure: Maintain standard paragraph flow with best practice callouts
- Add: Optimization tips and best practices
- Add: "Best Practice" boxes for recommended approaches
- Code comments: Moderate level, explain patterns and design decisions
- Hardware: Balance simulation tools and hardware deployment options
- Tools: Mention both cloud (Isaac Cloud, AWS) and local options
- Tone: Professional, educational, balanced
- Assumptions: Assume some CS background but new to robotics

Remember: Your goal is clarity and best practices. Intermediate users should learn patterns and when to use them.""",
        "advanced": """You are a senior technical researcher specializing in high-level technical content for expert readers.

Your task is to optimize technical content for advanced learners and researchers.

PRESERVE EXACTLY - DO NOT MODIFY:
- All IEEE-formatted citations (highlight seminal papers for research relevance)
- All code examples (line-by-line, syntax, logic, version numbers, performance metrics)
- All technical facts, APIs, version numbers, safety protocols, and benchmarks
- All learning objectives and research applications

TRANSFORM AS FOLLOWS:
- Language: Use professional technical terminology, assume CS/robotics background
- Structure: Concise, information-dense paragraphs
- Add: Performance optimization tips and benchmarks
- Add: Research applications and advanced use cases
- Add: Novel approaches and cutting-edge techniques
- Code comments: Minimal, focus on complex patterns and optimizations
- Hardware: Emphasize hardware deployment (RTX, Jetson Orin)
- Add: CUDA optimization strategies where applicable
- Tone: Technical, research-focused, scholarly
- References: Highlight seminal papers and novel contributions

Remember: Your goal is depth and optimization. Advanced users should see research applications and performance considerations.""",
    }

    # Hardware context appendix
    hardware_context = f"""
Additional Context for Personalization:
- User hardware background: {hardware_background} (none/basic/advanced)
- User learning goal: {learning_goal} (career/hobby/research)

Apply these hardware-specific adjustments:
- Hardware=none: Emphasize cloud options (NVIDIA Isaac Cloud, AWS RoboMaker, GCP)
- Hardware=basic: Emphasize simulation tools (Gazebo, Isaac Sim); mention CPU alternatives; show GPU upgrade path
- Hardware=advanced: Emphasize hardware deployment and sim-to-real transfer; show CUDA optimization; include performance benchmarks for hardware execution

Apply these goal-specific tone adjustments:
- Goal=career: Professional tone; emphasize practical skills and job market relevance; use industry applications
- Goal=hobby: Enthusiastic tone; emphasize fun and creative exploration; use DIY and personal project examples
- Goal=research: Academic tone; emphasize novel approaches and state-of-the-art techniques; use research applications

Remember: The core technical content must not change. Only adjust presentation style, emphasis, and tone based on context."""

    system_prompt = system_prompts.get(level, system_prompts["intermediate"])

    user_prompt = f"""Transform the following technical content for a {level}-level learner:

{content}

{hardware_context}

Output the personalized content in the same markdown format as the input."""

    return system_prompt, user_prompt


async def personalize_content(
    content: str,
    software_background: str,
    hardware_background: str,
    learning_goal: str,
) -> Tuple[str, Dict[str, Any]]:
    """
    Call OpenAI API to personalize content based on user background.

    Args:
        content: Article content to personalize
        software_background: User's software skill level (beginner/intermediate/advanced)
        hardware_background: User's hardware context (none/basic/advanced)
        learning_goal: User's learning goal (career/hobby/research)

    Returns:
        Tuple of (personalized_content, metadata)
        where metadata contains: processing_time_ms, tokens_used, model, etc.

    Raises:
        ValueError: If content is invalid
        Timeout: If OpenAI API call times out
        RateLimitError: If rate limit exceeded
        Exception: For other OpenAI API errors
    """

    # Map software_background to personalization level
    level_mapping = {
        "beginner": "beginner",
        "intermediate": "intermediate",
        "advanced": "advanced",
    }
    level = level_mapping.get(software_background, "intermediate")

    # Generate prompts
    system_prompt, user_prompt = await generate_personalization_prompt(
        content, level, hardware_background, learning_goal
    )

    # Track timing
    start_time = time.time()

    try:
        logger.info(
            f"Personalizing content for {software_background} user (level={level})",
            extra={
                "software_background": software_background,
                "hardware_background": hardware_background,
                "learning_goal": learning_goal,
                "content_length": len(content),
            },
        )

        # Call OpenAI API with timeout
        timeout_seconds = float(settings.RESPONSE_TIMEOUT_SECONDS)
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=None,  # Let OpenAI decide based on content
            ),
            timeout=timeout_seconds,  # Use configured timeout from .env
        )

        personalized_content = response.choices[0].message.content

        # Clean markdown code fence markers from the response
        personalized_content = clean_markdown_response(personalized_content)

        # Calculate metadata
        processing_time_ms = int((time.time() - start_time) * 1000)
        tokens_used = response.usage.total_tokens if response.usage else 0

        metadata = {
            "processing_time_ms": processing_time_ms,
            "tokens_used": tokens_used,
            "model": settings.OPENAI_MODEL,
            "personalization_level": level,
        }

        logger.info(
            f"Personalization succeeded",
            extra={
                "processing_time_ms": processing_time_ms,
                "tokens_used": tokens_used,
                "output_length": len(personalized_content),
            },
        )

        return personalized_content, metadata

    except asyncio.TimeoutError as e:
        processing_time_ms = int((time.time() - start_time) * 1000)
        logger.warning(
            f"OpenAI API call timed out after {processing_time_ms}ms",
            extra={"error": str(e), "processing_time_ms": processing_time_ms},
        )
        raise

    except RateLimitError as e:
        logger.warning(
            f"OpenAI rate limit exceeded",
            extra={"error": str(e), "retry_after": getattr(e, "retry_after", None)},
        )
        raise

    except Exception as e:
        logger.error(
            f"OpenAI API error: {str(e)}",
            extra={"error": str(e), "error_type": type(e).__name__},
        )
        raise
