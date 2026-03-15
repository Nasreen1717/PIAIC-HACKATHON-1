"""Unit tests for authentication endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.db.models import Base, User, UserBackground
from app.security import hash_password, verify_password, create_access_token, verify_token


# Test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    yield async_session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(test_db):
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestPasswordSecurity:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 20

    def test_verify_password(self):
        """Test password verification."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False


class TestTokenManagement:
    """Test JWT token creation and verification."""

    def test_create_access_token(self):
        """Test token creation."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_token(self):
        """Test token verification with valid token."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        payload = verify_token(token)
        assert payload is not None
        assert payload.get("sub") == "test@example.com"

    def test_verify_invalid_token(self):
        """Test token verification with invalid token."""
        payload = verify_token("invalid.token.here")
        assert payload is None

    def test_verify_expired_token(self):
        """Test token verification with expired token."""
        from datetime import datetime, timedelta
        from jose import jwt
        from app.security import JWT_SECRET, JWT_ALGORITHM

        # Create expired token
        to_encode = {"sub": "test@example.com", "exp": datetime.utcnow() - timedelta(hours=1)}
        token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

        payload = verify_token(token)
        assert payload is None


@pytest.mark.asyncio
class TestSignup:
    """Test signup endpoint."""

    async def test_signup_success(self, client):
        """Test successful signup."""
        response = await client.post(
            "/api/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "SecurePassword123",
                "full_name": "New User",
                "python_level": "beginner",
                "learning_goal": "Learn ROS",
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 7 * 24 * 60 * 60

    async def test_signup_duplicate_email(self, client):
        """Test signup with duplicate email."""
        email = "duplicate@example.com"

        # First signup
        await client.post(
            "/api/auth/signup",
            json={
                "email": email,
                "password": "SecurePassword123",
                "full_name": "User One",
            }
        )

        # Second signup with same email
        response = await client.post(
            "/api/auth/signup",
            json={
                "email": email,
                "password": "DifferentPassword123",
                "full_name": "User Two",
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    async def test_signup_invalid_password(self, client):
        """Test signup with short password."""
        response = await client.post(
            "/api/auth/signup",
            json={
                "email": "user@example.com",
                "password": "short",
                "full_name": "User",
            }
        )

        assert response.status_code == 422

    async def test_signup_invalid_email(self, client):
        """Test signup with invalid email."""
        response = await client.post(
            "/api/auth/signup",
            json={
                "email": "not-an-email",
                "password": "SecurePassword123",
                "full_name": "User",
            }
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestSignin:
    """Test signin endpoint."""

    async def test_signin_success(self, client):
        """Test successful signin."""
        # Create user first
        await client.post(
            "/api/auth/signup",
            json={
                "email": "user@example.com",
                "password": "SecurePassword123",
                "full_name": "User",
            }
        )

        # Sign in
        response = await client.post(
            "/api/auth/signin",
            json={
                "email": "user@example.com",
                "password": "SecurePassword123",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_signin_remember_me(self, client):
        """Test signin with remember_me flag."""
        await client.post(
            "/api/auth/signup",
            json={
                "email": "user@example.com",
                "password": "SecurePassword123",
                "full_name": "User",
            }
        )

        response = await client.post(
            "/api/auth/signin",
            json={
                "email": "user@example.com",
                "password": "SecurePassword123",
                "remember_me": True,
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["expires_in"] == 30 * 24 * 60 * 60  # 30 days

    async def test_signin_invalid_password(self, client):
        """Test signin with wrong password."""
        await client.post(
            "/api/auth/signup",
            json={
                "email": "user@example.com",
                "password": "SecurePassword123",
                "full_name": "User",
            }
        )

        response = await client.post(
            "/api/auth/signin",
            json={
                "email": "user@example.com",
                "password": "WrongPassword123",
            }
        )

        assert response.status_code == 401

    async def test_signin_user_not_found(self, client):
        """Test signin with non-existent email."""
        response = await client.post(
            "/api/auth/signin",
            json={
                "email": "nonexistent@example.com",
                "password": "SecurePassword123",
            }
        )

        assert response.status_code == 401
