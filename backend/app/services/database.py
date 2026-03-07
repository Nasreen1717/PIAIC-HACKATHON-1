"""
Database service for managing connections, sessions, and operations.

Provides connection pooling and async session management for SQLAlchemy.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings


class DatabaseService:
    """Manages database connections and sessions."""

    def __init__(self):
        """Initialize database engine and session factory."""
        # Convert DATABASE_URL to asyncpg-compatible format
        # Replace postgresql+asyncpg URL parameters that asyncpg doesn't understand
        url = settings.DATABASE_URL
        # Remove sslmode and channel_binding from query string (asyncpg handles SSL differently)
        url = url.replace("?sslmode=require&channel_binding=require", "")

        self.engine = create_async_engine(
            url,
            echo=settings.DEBUG,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"ssl": True},  # Enable SSL for asyncpg
        )
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    async def get_session(self) -> AsyncSession:
        """
        Get an async database session.

        Yields:
            AsyncSession: Database session for queries.
        """
        async with self.async_session_maker() as session:
            yield session

    async def create_tables(self):
        """Create all database tables."""
        from app.db.models import Base

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        """Drop all database tables (for testing)."""
        from app.db.models import Base

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def close(self):
        """Close database engine."""
        await self.engine.dispose()

    async def create_session(self, session_id: str, created_at: str) -> None:
        """
        Create a new conversation session.

        Args:
            session_id: Unique session identifier
            created_at: ISO format creation timestamp (string)
        """
        from app.db.models import Conversation
        from uuid import uuid4
        from datetime import datetime
        import logging

        logger = logging.getLogger(__name__)

        try:
            async with self.async_session_maker() as session:
                # Parse ISO string to datetime object
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

                conversation = Conversation(
                    id=str(uuid4()),
                    session_id=session_id,
                    created_at=created_dt,
                    updated_at=created_dt,
                )
                session.add(conversation)
                await session.commit()
        except Exception as e:
            logger.error(f"Database error creating session: {str(e)}", exc_info=True)
            raise Exception(f"Failed to create session: {str(e)}")

    async def store_message(
        self,
        session_id: str,
        role: str,
        content: str,
        citations: list = None,
    ) -> None:
        """
        Store a message (user or assistant) to conversation history.

        Args:
            session_id: Conversation session ID
            role: "user" or "assistant"
            content: Message content
            citations: Optional list of citation data
        """
        from app.db.models import Message, Conversation
        from datetime import datetime
        from uuid import uuid4

        try:
            async with self.async_session_maker() as session:
                # Get or create conversation
                result = await session.execute(
                    __import__("sqlalchemy").select(Conversation).where(
                        Conversation.session_id == session_id
                    )
                )
                conversation = result.scalar_one_or_none()

                if not conversation:
                    now = datetime.now()
                    conversation = Conversation(
                        id=str(uuid4()),
                        session_id=session_id,
                        created_at=now,
                        updated_at=now,
                    )
                    session.add(conversation)
                    await session.flush()

                # Store message
                import json
                now = datetime.now()

                message = Message(
                    id=str(uuid4()),
                    conversation_id=conversation.id,
                    role=role,
                    content=content,
                    message_metadata={"citations": citations} if citations else {},
                    created_at=now,
                )
                session.add(message)

                # Update conversation timestamp
                conversation.updated_at = now

                await session.commit()
        except Exception as e:
            raise Exception(f"Failed to store message: {str(e)}")

    async def get_conversation_history(self, session_id: str) -> dict:
        """
        Retrieve conversation history for a session.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with session metadata and messages, or None if not found
        """
        from app.db.models import Conversation, Message
        from sqlalchemy import select

        try:
            async with self.async_session_maker() as session:
                # Get conversation
                result = await session.execute(
                    select(Conversation).where(Conversation.session_id == session_id)
                )
                conversation = result.scalar_one_or_none()

                if not conversation:
                    return None

                # Get messages
                result = await session.execute(
                    select(Message)
                    .where(Message.conversation_id == conversation.id)
                    .order_by(Message.created_at)
                )
                messages = result.scalars().all()

                # Format response
                return {
                    "session": {
                        "session_id": conversation.session_id,
                        "message_count": len(messages),
                        "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
                        "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
                    },
                    "messages": [
                        {
                            "id": msg.id,
                            "role": msg.role,
                            "content": msg.content,
                            "citations": msg.message_metadata.get("citations") if msg.message_metadata else None,
                            "created_at": msg.created_at.isoformat() if msg.created_at else None,
                        }
                        for msg in messages
                    ],
                }
        except Exception as e:
            raise Exception(f"Failed to retrieve conversation history: {str(e)}")


# Global instance
database_service = DatabaseService()
db_service = database_service
