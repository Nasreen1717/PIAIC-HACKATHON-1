"""
Content personalization API endpoint.

Handles personalization requests and returns personalized content.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from openai import RateLimitError
import asyncio

from app.db.models import User
from app.schemas.personalize import PersonalizeRequest, PersonalizeResponse
from app.routes.auth import get_current_user
from app.services.openai_service import personalize_content

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/personalize", tags=["personalization"])


@router.post("", response_model=PersonalizeResponse, status_code=status.HTTP_200_OK)
async def personalize(
    request: PersonalizeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
) -> PersonalizeResponse:
    """
    Personalize article content based on user's background.

    Transforms article content to match the user's technical skill level,
    hardware context, and learning goals, while preserving all citations
    and code examples.

    Args:
        request: PersonalizeRequest with content and context
        current_user: Current authenticated user (from JWT token)

    Returns:
        PersonalizeResponse with personalized content and metadata

    Raises:
        HTTPException 400: Invalid content (empty, too long)
        HTTPException 401: Invalid/missing JWT token
        HTTPException 429: Rate limited by OpenAI API
        HTTPException 500: OpenAI API error or other server error
    """

    # Validate request content
    if not request.content or not request.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content cannot be empty",
        )

    if len(request.content) > 50000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content exceeds maximum length (50,000 characters)",
        )

    # Get user's background from request, then profile, then defaults
    software_background = (
        request.software_background or
        (current_user.background.software_background if current_user.background else None) or
        "intermediate"
    )
    hardware_background = (
        request.hardware_background if request.hardware_background else "none"
    )
    learning_goal = request.learning_goal if request.learning_goal else "career"

    logger.info(
        f"Personalizing content for user {current_user.email}",
        extra={
            "user_id": current_user.id,
            "software_background": software_background,
            "hardware_background": hardware_background,
            "learning_goal": learning_goal,
            "content_length": len(request.content),
        },
    )

    try:
        # Call personalization service
        personalized_content, metadata = await personalize_content(
            content=request.content,
            software_background=software_background,
            hardware_background=hardware_background,
            learning_goal=learning_goal,
        )

        # Map software_background to personalization_level
        level_mapping = {
            "beginner": "beginner",
            "intermediate": "intermediate",
            "advanced": "advanced",
        }
        personalization_level = level_mapping.get(software_background, "intermediate")

        logger.info(
            f"Personalization completed for user {current_user.email}",
            extra={
                "user_id": current_user.id,
                "processing_time_ms": metadata.get("processing_time_ms"),
                "tokens_used": metadata.get("tokens_used"),
            },
        )

        return PersonalizeResponse(
            personalized_content=personalized_content,
            personalization_level=personalization_level,
            metadata=metadata,
        )

    except asyncio.TimeoutError:
        logger.error(
            f"OpenAI API timeout for user {current_user.email}",
            extra={"user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Personalization service timeout. Please try again.",
        )

    except RateLimitError as e:
        logger.warning(
            f"OpenAI rate limit for user {current_user.email}",
            extra={"user_id": current_user.id, "retry_after": getattr(e, "retry_after", None)},
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Service is temporarily busy. Please try again in a moment.",
            headers={"Retry-After": str(getattr(e, "retry_after", 60))},
        )

    except Exception as e:
        logger.error(
            f"Personalization error for user {current_user.email}: {str(e)}",
            extra={
                "user_id": current_user.id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Personalization failed. Please try again.",
        )
