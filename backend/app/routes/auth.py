"""Authentication routes for signup, signin, profile, and signout."""
from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import timedelta
from typing import Optional

from app.db.models import User, UserBackground
from app.schemas.auth import (
    SignupRequest,
    SigninRequest,
    TokenResponse,
    UserDetailResponse,
    UserUpdateRequest,
    SignoutResponse,
)
from app.security import hash_password, verify_password, create_access_token, extract_email_from_token
from app.services.database import database_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


async def get_db():
    """Dependency to get database session."""
    async with database_service.async_session_maker() as session:
        yield session


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token."""
    import logging
    logger = logging.getLogger(__name__)

    # Extract token from Authorization header manually
    auth_header = request.headers.get("Authorization")
    logger.info(f"Authorization header: {auth_header}")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ")[1]
    logger.info(f"Extracted token: {token[:20]}...")
    email = extract_email_from_token(token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(User)
        .where(User.email == email)
        .options(selectinload(User.background))
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Register a new user account.

    Creates a new user with email, password, and optional background questionnaire.
    Returns JWT token for automatic signin after signup.

    Args:
        request: Signup request with email, password, and optional background info
        db: Database session

    Returns:
        TokenResponse with JWT access token

    Raises:
        HTTPException: 400 if email already exists
        HTTPException: 500 on database error
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    try:
        # Create new user
        new_user = User(
            email=request.email,
            password_hash=hash_password(request.password),
            full_name=request.full_name,
        )
        db.add(new_user)
        await db.flush()  # Get user ID before commit

        # Create user background if provided
        if any([
            request.software_background,
            request.hardware_background,
            request.ros_experience,
            request.python_level,
            request.learning_goal,
            request.available_hardware,
        ]):
            background = UserBackground(
                user_id=new_user.id,
                software_background=request.software_background,
                hardware_background=request.hardware_background,
                ros_experience=request.ros_experience,
                python_level=request.python_level,
                learning_goal=request.learning_goal,
                available_hardware=request.available_hardware,
            )
            db.add(background)

        await db.commit()

        # Generate token
        access_token = create_access_token(data={"sub": new_user.email})

        # Calculate expires_in (in seconds)
        expires_in = 7 * 24 * 60 * 60  # 7 days

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account",
        )


@router.post("/signin", response_model=TokenResponse)
async def signin(request: SigninRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Authenticate user with email and password.

    Args:
        request: Signin request with email, password, and optional remember_me flag
        db: Database session

    Returns:
        TokenResponse with JWT access token

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )

    # Determine token expiration based on remember_me flag
    if request.remember_me:
        expires_delta = timedelta(days=30)
        expires_in = 30 * 24 * 60 * 60  # 30 days in seconds
    else:
        expires_delta = timedelta(days=7)
        expires_in = 7 * 24 * 60 * 60  # 7 days in seconds

    # Generate token
    access_token = create_access_token(data={"sub": user.email}, expires_delta=expires_delta)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_profile(user: User = Depends(get_current_user)) -> UserDetailResponse:
    """Get current authenticated user's profile.

    Requires valid JWT token in Authorization header.

    Args:
        user: Current authenticated user (injected via dependency)

    Returns:
        UserDetailResponse with user info and background questionnaire
    """
    try:
        # Build background response if it exists
        background_response = None
        if user.background:
            background_response = {
                "id": user.background.id,
                "user_id": user.background.user_id,
                "software_background": user.background.software_background,
                "hardware_background": user.background.hardware_background,
                "ros_experience": user.background.ros_experience,
                "python_level": user.background.python_level,
                "learning_goal": user.background.learning_goal,
                "available_hardware": user.background.available_hardware,
                "created_at": user.background.created_at,
                "updated_at": user.background.updated_at,
            }

        response = UserDetailResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at,
            is_active=user.is_active,
            background=background_response,
        )
        return response
    except Exception as e:
        import traceback
        logger = __import__('logging').getLogger(__name__)
        logger.error(f"Error in get_current_user_profile: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user profile: {str(e)}"
        )


@router.put("/me", response_model=UserDetailResponse)
async def update_current_user_profile(
    request: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserDetailResponse:
    """Update current user's profile information.

    Requires valid JWT token. Updates background questionnaire if provided.

    Args:
        request: Update request with new profile fields
        user: Current authenticated user (injected via dependency)
        db: Database session

    Returns:
        Updated UserDetailResponse

    Raises:
        HTTPException: 500 on database error
    """
    try:
        # Update user fields
        if request.full_name is not None:
            user.full_name = request.full_name

        # Update or create background info
        if any([
            request.software_background is not None,
            request.hardware_background is not None,
            request.ros_experience is not None,
            request.python_level is not None,
            request.learning_goal is not None,
            request.available_hardware is not None,
        ]):
            if user.background is None:
                user.background = UserBackground(user_id=user.id)
                db.add(user.background)

            if request.software_background is not None:
                user.background.software_background = request.software_background
            if request.hardware_background is not None:
                user.background.hardware_background = request.hardware_background
            if request.ros_experience is not None:
                user.background.ros_experience = request.ros_experience
            if request.python_level is not None:
                user.background.python_level = request.python_level
            if request.learning_goal is not None:
                user.background.learning_goal = request.learning_goal
            if request.available_hardware is not None:
                user.background.available_hardware = request.available_hardware

        await db.commit()

        # Refresh user with eager-loaded background
        result = await db.execute(
            select(User)
            .where(User.id == user.id)
            .options(selectinload(User.background))
        )
        user = result.scalar_one_or_none()

        # Build background response if it exists
        background_response = None
        if user and user.background:
            background_response = {
                "id": user.background.id,
                "user_id": user.background.user_id,
                "software_background": user.background.software_background,
                "hardware_background": user.background.hardware_background,
                "ros_experience": user.background.ros_experience,
                "python_level": user.background.python_level,
                "learning_goal": user.background.learning_goal,
                "available_hardware": user.background.available_hardware,
                "created_at": user.background.created_at,
                "updated_at": user.background.updated_at,
            }

        return UserDetailResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at,
            is_active=user.is_active,
            background=background_response,
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile",
        )


@router.post("/signout", response_model=SignoutResponse)
async def signout(user: User = Depends(get_current_user)) -> SignoutResponse:
    """Sign out the current user.

    Requires valid JWT token. Token validation is done server-side,
    but clients should also clear the token from localStorage.

    Args:
        user: Current authenticated user (injected via dependency)

    Returns:
        SignoutResponse with success message
    """
    return SignoutResponse(message="Successfully signed out")
