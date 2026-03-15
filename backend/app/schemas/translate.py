"""Schemas for translation API."""

from pydantic import BaseModel, Field
from typing import Optional


class TranslateRequest(BaseModel):
    """Request to translate text."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Text to translate"
    )
    source_lang: str = Field(
        default="en",
        description="Source language code (ISO 639-1)"
    )
    target_lang: str = Field(
        default="ur",
        description="Target language code (only 'ur' supported)"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session identifier"
    )


class TranslateResponse(BaseModel):
    """Response from translation endpoint."""

    translated_text: str = Field(
        ...,
        description="Translated text"
    )
    detected_lang: str = Field(
        ...,
        description="Language detected in source"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0)"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Echo back of request session_id"
    )
