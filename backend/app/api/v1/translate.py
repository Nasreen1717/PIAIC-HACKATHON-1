"""
Translation API endpoints.

Provides POST /api/v1/translate endpoint for translating article content.
Requires JWT authentication via Authorization header.
Uses OpenAI API to translate content to Urdu.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from openai import AsyncOpenAI

from app.db.models import User
from app.routes.auth import get_current_user, get_db
from app.schemas.translate import TranslateRequest, TranslateResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/translate", tags=["translate"])

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def translate_text_openai(text: str, target_lang: str = "ur") -> str:
    """
    Translate text to Urdu using OpenAI API.

    Args:
        text: English text to translate
        target_lang: Target language code (currently only 'ur' for Urdu)

    Returns:
        Translated Urdu text

    Raises:
        Exception: If OpenAI API call fails
    """
    if target_lang != "ur":
        raise ValueError(f"Unsupported target language: {target_lang}")

    system_prompt = """You are a professional translator. Translate the provided English text to Urdu.
Important:
- Maintain the original meaning and tone
- PRESERVE ALL HTML TAGS EXACTLY as they appear (<h1>, <h2>, <h3>, <p>, <ul>, <li>, <strong>, <em>, <code>, <pre>, etc.)
- Only translate the text content INSIDE the tags, never modify or remove tags
- Preserve any formatting, code blocks, code placeholders [CODE_BLOCK_*], or special characters
- Translate only the text content, not code or technical terms where English is standard
- Keep the exact same HTML structure and layout
- Respond ONLY with the translated HTML, no explanations or additional content"""

    user_message = f"Translate the following English text to Urdu:\n\n{text}"

    try:
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,  # Lower temperature for more consistent translations
            max_tokens=min(len(text) * 2, 4000),  # Urdu text is typically longer
        )

        translated_text = response.choices[0].message.content.strip()
        logger.info(f"Successfully translated {len(text)} characters to Urdu")
        return translated_text

    except Exception as e:
        logger.error(f"OpenAI translation error: {str(e)}")
        raise


@router.post("/", response_model=TranslateResponse)
async def translate(
    request: TranslateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TranslateResponse:
    """
    Translate article content to target language.

    Requires valid JWT authentication token in Authorization header.

    Args:
        request: TranslateRequest with text to translate
        current_user: Authenticated user (guaranteed by get_current_user dependency)
        db: Database session (for potential future user tracking)

    Returns:
        TranslateResponse with translated text, language detection, and confidence

    Raises:
        HTTPException: 400 for invalid input, 401 for unauthenticated, 503 for service error
    """
    try:
        # Validate input
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )

        if len(request.text) > 50000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text too long (max 50000 chars)"
            )

        if request.target_lang not in ["ur"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported target language"
            )

        logger.info(f"Translation request from user {current_user.email}: {len(request.text)} chars to {request.target_lang}")

        # Call OpenAI API to translate
        translated_text = await translate_text_openai(
            text=request.text,
            target_lang=request.target_lang
        )

        return TranslateResponse(
            translated_text=translated_text,
            detected_lang=request.source_lang,
            confidence=0.95,  # OpenAI translations are highly reliable
            session_id=request.session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Translation service error: {str(e)}"
        )
