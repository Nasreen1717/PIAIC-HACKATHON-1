"""Pydantic schemas for authentication endpoints."""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class SignupRequest(BaseModel):
    """Request body for user signup."""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters, contain 1 letter and 1 number")
    full_name: str = Field(..., min_length=2, max_length=255)
    software_background: Optional[str] = None
    hardware_background: Optional[str] = None
    ros_experience: Optional[str] = None
    python_level: Optional[str] = None
    learning_goal: Optional[str] = None
    available_hardware: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password contains at least 1 letter and 1 number."""
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('Password must contain at least 1 letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least 1 number')
        return v


class SigninRequest(BaseModel):
    """Request body for user signin."""
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """User information response."""
    id: int
    email: str
    full_name: Optional[str]
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class UserBackgroundResponse(BaseModel):
    """User background/questionnaire response."""
    id: int
    user_id: int
    software_background: Optional[str]
    hardware_background: Optional[str]
    ros_experience: Optional[str]
    python_level: Optional[str]
    learning_goal: Optional[str]
    available_hardware: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserDetailResponse(BaseModel):
    """Complete user profile with background."""
    id: int
    email: str
    full_name: Optional[str]
    created_at: datetime
    is_active: bool
    background: Optional[UserBackgroundResponse]

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    """Request to update user profile."""
    full_name: Optional[str] = None
    software_background: Optional[str] = None
    hardware_background: Optional[str] = None
    ros_experience: Optional[str] = None
    python_level: Optional[str] = None
    learning_goal: Optional[str] = None
    available_hardware: Optional[str] = None


class SignoutResponse(BaseModel):
    """Signout response."""
    message: str = "Successfully signed out"
