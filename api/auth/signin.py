"""
POST /api/auth/signin - User authentication endpoint

Authenticates user with email and password.
Returns JWT token on success (7 days or 30 days with remember_me).
"""

import json
import re
from http import HTTPStatus
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _middleware import (
    verify_password,
    generate_jwt_token,
    get_db_connection,
    get_cors_headers,
    parse_json_body,
    error_response,
    success_response,
)


EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


def validate_email(email: str) -> bool:
    """Validate email format."""
    return bool(re.match(EMAIL_REGEX, email))


def validate_request(body: dict) -> str:
    """Validate signin request.

    Returns:
        Error message if invalid, empty string if valid
    """
    email = body.get("email", "").strip()
    password = body.get("password", "").strip()

    if not email:
        return "Email is required"
    if not validate_email(email):
        return "Invalid email format"

    if not password:
        return "Password is required"

    return ""


async def handler(request):
    """Handle signin requests."""

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

        # Validate request
        validation_error = validate_request(body)
        if validation_error:
            data, status, headers = error_response(validation_error, 400)
            return (json.dumps(data), status, headers)

        email = body.get("email", "").strip()
        password = body.get("password", "").strip()
        remember_me = body.get("remember_me", False)

        # Get database connection
        conn = await get_db_connection()

        try:
            # Find user by email
            user = await conn.fetchrow(
                "SELECT id, email, password_hash FROM users WHERE email = $1 AND is_active = true",
                email
            )

            if not user:
                data, status, headers = error_response("Invalid email or password", 401)
                return (json.dumps(data), status, headers)

            # Verify password
            if not verify_password(password, user["password_hash"]):
                data, status, headers = error_response("Invalid email or password", 401)
                return (json.dumps(data), status, headers)

            # Generate JWT token
            token_data = generate_jwt_token(
                user["id"],
                user["email"],
                remember_me=remember_me
            )

            # Success response
            response_data = {
                "access_token": token_data["access_token"],
                "token_type": token_data["token_type"],
                "expires_in": token_data["expires_in"],
                "user_id": user["id"],
                "email": user["email"],
            }

            data, status, headers = success_response(response_data, 200)
            return (json.dumps(data), status, headers)

        finally:
            await conn.close()

    except Exception as e:
        print(f"❌ Signin error: {str(e)}")
        data, status, headers = error_response("Internal server error", 500)
        return (json.dumps(data), status, headers)
