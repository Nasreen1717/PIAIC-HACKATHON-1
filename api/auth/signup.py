"""
POST /api/auth/signup - User registration endpoint

Allows public signup with email, password, and optional background information.
Returns JWT token on success.
"""

import json
import re
from http import HTTPStatus
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _middleware import (
    hash_password,
    generate_jwt_token,
    get_db_connection,
    get_cors_headers,
    parse_json_body,
    error_response,
    success_response,
)


# Validation constraints
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
MIN_PASSWORD_LENGTH = 6
MAX_NAME_LENGTH = 255


def validate_email(email: str) -> bool:
    """Validate email format."""
    return bool(re.match(EMAIL_REGEX, email))


def validate_password(password: str) -> str:
    """Validate password requirements.

    Returns:
        Error message if invalid, empty string if valid
    """
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters"

    if not re.search(r"[a-zA-Z]", password):
        return "Password must contain at least 1 letter"

    if not re.search(r"[0-9]", password):
        return "Password must contain at least 1 number"

    return ""


def validate_request(body: dict) -> str:
    """Validate signup request.

    Returns:
        Error message if invalid, empty string if valid
    """
    # Required fields
    email = body.get("email", "").strip()
    password = body.get("password", "").strip()
    full_name = body.get("full_name", "").strip()

    if not email:
        return "Email is required"
    if not validate_email(email):
        return "Invalid email format"

    if not password:
        return "Password is required"
    pwd_error = validate_password(password)
    if pwd_error:
        return pwd_error

    if not full_name:
        return "Full name is required"
    if len(full_name) > MAX_NAME_LENGTH:
        return f"Full name cannot exceed {MAX_NAME_LENGTH} characters"

    return ""


async def handler(request):
    """Handle signup requests."""

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
        full_name = body.get("full_name", "").strip()

        # Optional background fields
        software_background = body.get("software_background", "beginner").lower()
        hardware_background = body.get("hardware_background", "none").lower()
        ros_experience = body.get("ros_experience", "none").lower()
        python_level = body.get("python_level", "beginner").lower()
        learning_goal = body.get("learning_goal", "career").lower()
        available_hardware = body.get("available_hardware", "")

        # Get database connection
        conn = await get_db_connection()

        try:
            # Check if email already exists
            existing_user = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1",
                email
            )

            if existing_user:
                data, status, headers = error_response("Email already registered", 409)
                return (json.dumps(data), status, headers)

            # Hash password
            password_hash = hash_password(password)

            # Create user
            user = await conn.fetchrow(
                """
                INSERT INTO users (email, password_hash, full_name, is_active)
                VALUES ($1, $2, $3, true)
                RETURNING id, email
                """,
                email, password_hash, full_name
            )

            user_id = user["id"]

            # Create user background profile (optional)
            try:
                await conn.execute(
                    """
                    INSERT INTO user_backgrounds
                    (user_id, software_background, hardware_background, ros_experience,
                     python_level, learning_goal, available_hardware)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    user_id, software_background, hardware_background, ros_experience,
                    python_level, learning_goal, available_hardware
                )
            except Exception as e:
                # Log but don't fail - background is optional
                print(f"⚠️  Failed to create user background: {str(e)}")

            # Generate JWT token
            token_data = generate_jwt_token(user_id, email, remember_me=False)

            # Success response
            response_data = {
                "access_token": token_data["access_token"],
                "token_type": token_data["token_type"],
                "expires_in": token_data["expires_in"],
                "user_id": user_id,
                "email": email,
            }

            data, status, headers = success_response(response_data, 201)
            return (json.dumps(data), status, headers)

        finally:
            await conn.close()

    except Exception as e:
        print(f"❌ Signup error: {str(e)}")
        data, status, headers = error_response("Internal server error", 500)
        return (json.dumps(data), status, headers)
