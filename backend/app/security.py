"""Security utilities for password hashing and JWT token handling."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
JWT_SECRET = settings.JWT_SECRET if hasattr(settings, 'JWT_SECRET') else "your-secret-key-change-in-production"
JWT_ALGORITHM = settings.JWT_ALGORITHM if hasattr(settings, 'JWT_ALGORITHM') else "HS256"
JWT_EXPIRATION_DAYS = settings.JWT_EXPIRATION_DAYS if hasattr(settings, 'JWT_EXPIRATION_DAYS') else 7
REMEMBER_ME_EXPIRATION_DAYS = settings.REMEMBER_ME_EXPIRATION_DAYS if hasattr(settings, 'REMEMBER_ME_EXPIRATION_DAYS') else 30


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.

    Args:
        data: Dictionary with user info (typically {"sub": email})
        expires_delta: Optional custom expiration time. Defaults to JWT_EXPIRATION_DAYS

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def extract_email_from_token(token: str) -> Optional[str]:
    """Extract email (subject) from a JWT token.

    Args:
        token: JWT token string

    Returns:
        Email if token is valid, None otherwise
    """
    payload = verify_token(token)
    if payload and "sub" in payload:
        return payload.get("sub")
    return None
