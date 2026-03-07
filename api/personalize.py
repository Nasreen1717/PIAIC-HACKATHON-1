"""
POST /api/personalize - Content personalization endpoint

Adapts learning content based on user's background and learning level.
Uses OpenAI to generate personalized explanations.
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
    get_db_connection,
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

# Learning level descriptions for prompting
LEVEL_DESCRIPTIONS = {
    "beginner": "a beginner with no prior experience in robotics or programming",
    "intermediate": "an intermediate learner with some programming or robotics background",
    "advanced": "an advanced learner with strong technical background",
}


def get_difficulty_prompt(level: str) -> str:
    """Get prompting guidance based on learning level."""
    return LEVEL_DESCRIPTIONS.get(level.lower(), LEVEL_DESCRIPTIONS["beginner"])


def personalize_content(content: str, learning_level: str, context: str = "") -> str:
    """Personalize learning content based on user's level.

    Args:
        content: Original learning content
        learning_level: User's learning level (beginner/intermediate/advanced)
        context: Optional context about user's background

    Returns:
        Personalized content
    """
    if not OpenAI or not OPENAI_API_KEY:
        raise ValueError("OpenAI API not configured")

    difficulty = get_difficulty_prompt(learning_level)

    client = OpenAI(api_key=OPENAI_API_KEY)

    system_prompt = f"""You are an expert robotics educator. Adapt the following learning content
for {difficulty}.
{f'User context: {context}' if context else ''}
Adjust the explanation level, add more examples if beginner, more technical depth if advanced.
Keep the core concepts accurate and clear."""

    message = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": f"Please personalize this content:\n\n{content}",
            },
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    return message.choices[0].message.content.strip()


async def handler(request):
    """Handle personalization requests."""

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

        user_id = payload.get("user_id")

        # Validate request
        content = body.get("content", "").strip()
        learning_level = body.get("learning_level", "beginner").strip().lower()

        if not content:
            data, status, headers = error_response("Content is required", 400)
            return (json.dumps(data), status, headers)

        if learning_level not in LEVEL_DESCRIPTIONS:
            data, status, headers = error_response(
                f"Invalid learning level. Must be one of: {', '.join(LEVEL_DESCRIPTIONS.keys())}",
                400,
            )
            return (json.dumps(data), status, headers)

        # Get user background if available
        user_context = ""
        try:
            conn = await get_db_connection()
            try:
                background = await conn.fetchrow(
                    "SELECT software_background, hardware_background, ros_experience FROM user_backgrounds WHERE user_id = $1",
                    user_id,
                )
                if background:
                    user_context = f"Software: {background['software_background']}, Hardware: {background['hardware_background']}, ROS: {background['ros_experience']}"
            finally:
                await conn.close()
        except Exception as e:
            print(f"⚠️  Could not fetch user background: {str(e)}")

        # Personalize content
        personalized = personalize_content(content, learning_level, user_context)

        # Success response
        response_data = {
            "original_content": content,
            "personalized_content": personalized,
            "learning_level": learning_level,
            "user_context": user_context,
        }

        data, status, headers = success_response(response_data, 200)
        return (json.dumps(data), status, headers)

    except ValueError as e:
        data, status, headers = error_response(str(e), 400)
        return (json.dumps(data), status, headers)
    except Exception as e:
        print(f"❌ Personalization error: {str(e)}")
        data, status, headers = error_response("Internal server error", 500)
        return (json.dumps(data), status, headers)
