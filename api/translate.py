"""
POST /api/translate - Translation endpoint

Translates text to specified language using OpenAI API.
Requires JWT authentication.
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _middleware import (
    verify_jwt_token,
    extract_token_from_header,
    get_cors_headers,
    parse_json_body,
    error_response,
    success_response,
)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def translate_text(text: str, target_language: str) -> str:
    """Translate text to target language using OpenAI.

    Args:
        text: Text to translate
        target_language: Target language (e.g., 'ur' for Urdu)

    Returns:
        Translated text
    """
    if not OpenAI or not OPENAI_API_KEY:
        raise ValueError("OpenAI API not configured")

    language_names = {
        "ur": "Urdu",
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "zh": "Chinese",
        "ar": "Arabic",
        "hi": "Hindi",
    }

    target_lang_name = language_names.get(target_language.lower(), target_language)

    client = OpenAI(api_key=OPENAI_API_KEY)

    message = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful translator. Translate the following text to {target_lang_name}. Return only the translated text without any explanation.",
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        temperature=0.3,
        max_tokens=1000,
    )

    return message.choices[0].message.content.strip()


async def handler(request):
    """Handle translation requests."""

    # Handle CORS preflight
    if request.method == "OPTIONS":
        headers = get_cors_headers()
        return ("", 204, headers)

    if request.method != "POST":
        data, status, headers = error_response("Method not allowed", 405)
        return (json.dumps(data), status, headers)

    try:
        # Parse request body
        body_text = request.get_body(as_text=True)
        body = parse_json_body(body_text)

        if not body:
            data, status, headers = error_response("Invalid JSON", 400)
            return (json.dumps(data), status, headers)

        # Check authentication
        auth_header = request.headers.get("Authorization", "")
        token = extract_token_from_header(auth_header)

        if not token:
            data, status, headers = error_response("Missing authorization token", 401)
            return (json.dumps(data), status, headers)

        payload = verify_jwt_token(token)
        if not payload:
            data, status, headers = error_response("Invalid or expired token", 401)
            return (json.dumps(data), status, headers)

        # Validate request
        text = body.get("text", "").strip()
        target_language = body.get("target_language", "ur").strip().lower()

        if not text:
            data, status, headers = error_response("Text is required", 400)
            return (json.dumps(data), status, headers)

        if not target_language:
            data, status, headers = error_response("Target language is required", 400)
            return (json.dumps(data), status, headers)

        # Translate text
        translated = translate_text(text, target_language)

        # Success response
        response_data = {
            "original_text": text,
            "translated_text": translated,
            "target_language": target_language,
        }

        data, status, headers = success_response(response_data, 200)
        return (json.dumps(data), status, headers)

    except ValueError as e:
        data, status, headers = error_response(str(e), 400)
        return (json.dumps(data), status, headers)
    except Exception as e:
        print(f"❌ Translation error: {str(e)}")
        data, status, headers = error_response("Internal server error", 500)
        return (json.dumps(data), status, headers)
