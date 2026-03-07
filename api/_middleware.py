"""
Shared middleware and utilities for Vercel serverless functions.

This module provides:
- Database connection pooling (Neon serverless driver)
- JWT token generation and verification
- CORS headers
- Password hashing with bcrypt
- Error response formatting
- Request body parsing
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import jwt
from passlib.context import CryptContext
import asyncpg
from http import HTTPStatus


# ============================================================================
# Configuration
# ============================================================================

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7  # Standard: 7 days
JWT_REMEMBER_ME_DAYS = 30  # Extended: 30 days with remember_me

DATABASE_URL = os.getenv("DATABASE_URL", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# Database Connection Pooling (Neon Serverless)
# ============================================================================

_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    """Get or create database connection pool using Neon serverless driver.

    Neon's serverless driver with pgBouncer connection pooling handles
    cold-start exhaustion and maintains persistent connections.
    """
    global _pool

    if _pool is None:
        try:
            _pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=1,
                max_size=10,
                max_queries=50000,
                max_inactive_connection_lifetime=300.0,  # 5 minutes
                server_settings={
                    "application_name": "thinkmesh-api",
                    "jit": "off",  # Disable JIT for serverless
                }
            )
        except Exception as e:
            raise RuntimeError(f"Failed to connect to database: {str(e)}")

    return _pool


async def close_db_pool() -> None:
    """Close the database connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def get_db_connection():
    """Get a single database connection from the pool."""
    pool = await get_db_pool()
    return await pool.acquire()


# ============================================================================
# JWT Token Management
# ============================================================================

def generate_jwt_token(
    user_id: int,
    email: str,
    remember_me: bool = False
) -> Dict[str, Any]:
    """Generate a JWT token for authenticated users.

    Args:
        user_id: The user's database ID
        email: The user's email address
        remember_me: If True, extend expiration to 30 days

    Returns:
        Dictionary with access_token, token_type, and expires_in
    """
    expiration_days = JWT_REMEMBER_ME_DAYS if remember_me else JWT_EXPIRATION_DAYS
    expiration_time = datetime.utcnow() + timedelta(days=expiration_days)

    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expiration_time,
        "iat": datetime.utcnow(),
    }

    access_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    expires_in_seconds = int(expiration_days * 24 * 60 * 60)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in_seconds,
    }


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token.

    Args:
        token: The JWT token string (without "Bearer " prefix)

    Returns:
        Decoded token payload if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token


def extract_token_from_header(auth_header: str) -> Optional[str]:
    """Extract JWT token from Authorization header.

    Expected format: "Bearer <token>"

    Args:
        auth_header: The Authorization header value

    Returns:
        Token string if valid format, None otherwise
    """
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]


# ============================================================================
# CORS Headers
# ============================================================================

def get_cors_headers() -> Dict[str, str]:
    """Generate CORS headers for serverless responses.

    Allows requests from the frontend URL with credentials.
    """
    return {
        "Access-Control-Allow-Origin": FRONTEND_URL,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,PATCH,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Max-Age": "86400",
    }


def handle_cors_preflight() -> Tuple[Dict[str, str], int]:
    """Handle CORS preflight (OPTIONS) requests.

    Returns:
        Tuple of (headers dict, status code)
    """
    return (get_cors_headers(), 204)


# ============================================================================
# Password Hashing & Verification
# ============================================================================

def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: The plaintext password

    Returns:
        Bcrypt-hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plaintext: str, hashed: str) -> bool:
    """Verify a plaintext password against its bcrypt hash.

    Args:
        plaintext: The plaintext password to verify
        hashed: The bcrypt-hashed password

    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plaintext, hashed)


# ============================================================================
# Error Response Formatting
# ============================================================================

def error_response(detail: str, status_code: int = 400) -> Tuple[Dict[str, Any], int]:
    """Format a consistent error response.

    Args:
        detail: Error message
        status_code: HTTP status code (400, 401, 409, 500, etc.)

    Returns:
        Tuple of (response body dict, status code)
    """
    headers = get_cors_headers()
    response = {
        "detail": detail,
        "status_code": status_code,
        "timestamp": datetime.utcnow().isoformat(),
    }
    return (response, status_code, headers)


def success_response(data: Dict[str, Any], status_code: int = 200) -> Tuple[Dict[str, Any], int]:
    """Format a consistent success response.

    Args:
        data: Response data
        status_code: HTTP status code (200, 201, etc.)

    Returns:
        Tuple of (response body dict, status code, headers dict)
    """
    headers = get_cors_headers()
    return (data, status_code, headers)


# ============================================================================
# Request Body Parsing
# ============================================================================

def parse_json_body(body: str) -> Optional[Dict[str, Any]]:
    """Parse a JSON request body.

    Args:
        body: The raw request body string

    Returns:
        Parsed JSON dict if valid, None if invalid
    """
    if not body:
        return None

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


# ============================================================================
# Initialization & Cleanup
# ============================================================================

async def initialize() -> None:
    """Initialize middleware (called on cold-start)."""
    try:
        pool = await get_db_pool()
        # Test connection
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        print("✅ Database pool initialized")
    except Exception as e:
        print(f"❌ Initialization error: {str(e)}")
        raise


async def cleanup() -> None:
    """Cleanup middleware (called on shutdown)."""
    try:
        await close_db_pool()
        print("✅ Database pool closed")
    except Exception as e:
        print(f"⚠️  Cleanup error: {str(e)}")
