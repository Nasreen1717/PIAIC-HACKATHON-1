"""
Pydantic schemas for content personalization feature.

Defines request/response models for the personalization endpoint.
"""

from typing import Any, Dict, Literal

from pydantic import BaseModel, Field


class PersonalizeRequest(BaseModel):
    """Request to personalize article content."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Article content to personalize (markdown)",
    )
    software_background: Literal["beginner", "intermediate", "advanced"] = Field(
        ..., description="User's software/technical skill level"
    )
    hardware_background: Literal["none", "basic", "advanced"] = Field(
        default="none", description="User's hardware background level"
    )
    learning_goal: Literal["career", "hobby", "research"] = Field(
        default="career", description="User's learning goal"
    )


class PersonalizeResponse(BaseModel):
    """Response with personalized content."""

    personalized_content: str = Field(..., description="Personalized markdown content")
    personalization_level: Literal["beginner", "intermediate", "advanced"] = Field(
        ..., description="Personalization level applied"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Processing metadata (processing_time_ms, tokens_used, etc.)",
    )
