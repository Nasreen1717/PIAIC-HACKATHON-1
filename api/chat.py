"""
POST /api/chat - RAG Chatbot endpoint

Provides an intelligent chatbot for answering questions about the course content.
Uses retrieval-augmented generation (RAG) with OpenAI.
Stores conversation history for context.
Requires JWT authentication.
"""

import json
import uuid
import sys
import os
from datetime import datetime

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

# System prompt for the RAG chatbot
SYSTEM_PROMPT = """You are an expert robotics and humanoid robotics teaching assistant.
Your role is to help students understand concepts related to robotics, ROS (Robot Operating System),
and humanoid robot development.

Guidelines:
1. Provide clear, concise explanations suitable for learners
2. Use examples from robotics when relevant
3. If you don't know the answer, acknowledge it and suggest resources
4. Ask clarifying questions if the student's question is ambiguous
5. Encourage hands-on learning and experimentation

Always be helpful, patient, and encouraging."""


def generate_chat_response(message: str, conversation_history: list) -> str:
    """Generate a response using OpenAI with conversation history.

    Args:
        message: User's current message
        conversation_history: List of previous messages in conversation

    Returns:
        Assistant's response
    """
    if not OpenAI or not OPENAI_API_KEY:
        raise ValueError("OpenAI API not configured")

    # Build messages for OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history (limit to last 10 messages for context window)
    for msg in conversation_history[-20:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("message", "")})

    # Add current message
    messages.append({"role": "user", "content": message})

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=1000,
    )

    return response.choices[0].message.content.strip()


async def handler(request):
    """Handle chat requests."""

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
        message = body.get("message", "").strip()
        conversation_id = body.get("conversation_id", str(uuid.uuid4()))

        if not message:
            data, status, headers = error_response("Message is required", 400)
            return (json.dumps(data), status, headers)

        # Get conversation history
        conn = await get_db_connection()

        try:
            # Fetch previous messages in this conversation
            history = await conn.fetch(
                """SELECT role, message FROM conversation_histories
                   WHERE user_id = $1 AND conversation_id = $2
                   ORDER BY created_at ASC""",
                user_id,
                conversation_id,
            )

            # Generate response
            assistant_message = generate_chat_response(
                message, [{"role": h["role"], "message": h["message"]} for h in history]
            )

            # Store user message in history
            await conn.execute(
                """INSERT INTO conversation_histories
                   (user_id, conversation_id, role, message, created_at)
                   VALUES ($1, $2, $3, $4, $5)""",
                user_id,
                conversation_id,
                "user",
                message,
                datetime.utcnow(),
            )

            # Store assistant response in history
            await conn.execute(
                """INSERT INTO conversation_histories
                   (user_id, conversation_id, role, message, created_at)
                   VALUES ($1, $2, $3, $4, $5)""",
                user_id,
                conversation_id,
                "assistant",
                assistant_message,
                datetime.utcnow(),
            )

            # Success response
            response_data = {
                "conversation_id": conversation_id,
                "user_message": message,
                "assistant_message": assistant_message,
                "message_count": len(history) + 2,
            }

            data, status, headers = success_response(response_data, 200)
            return (json.dumps(data), status, headers)

        finally:
            await conn.close()

    except ValueError as e:
        data, status, headers = error_response(str(e), 400)
        return (json.dumps(data), status, headers)
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        data, status, headers = error_response("Internal server error", 500)
        return (json.dumps(data), status, headers)
