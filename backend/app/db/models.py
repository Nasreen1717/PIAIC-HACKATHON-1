"""
SQLAlchemy models for RAG Chatbot.

Defines the data schema for:
- Conversations: User conversation sessions
- Messages: Individual chat messages (questions and answers)
- Citations: Sources referenced in answers
- Users: User accounts with authentication
- UserBackgrounds: User questionnaire and background information
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Float, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Conversation(Base):
    """Represents a conversation session for a user."""

    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True, unique=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    message_count = Column(Integer, default=0)

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, session_id={self.session_id})>"


class Message(Base):
    """Represents a single message in a conversation."""

    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), index=True)
    role = Column(String, index=True)  # "user" or "assistant"
    content = Column(Text)
    message_metadata = Column(JSON, default=dict, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    citations = relationship("Citation", back_populates="message", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"


class Citation(Base):
    """Represents a citation/source reference for an answer."""

    __tablename__ = "citations"

    id = Column(String, primary_key=True, index=True)
    message_id = Column(String, ForeignKey("messages.id"), index=True)
    chapter_number = Column(Integer)
    section_id = Column(String)
    section_title = Column(String)
    source_text = Column(Text)
    similarity_score = Column(Float)  # Vector similarity score
    chunk_id = Column(String, index=True)  # Reference to Qdrant point ID
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    message = relationship("Message", back_populates="citations")

    def __repr__(self) -> str:
        return f"<Citation(id={self.id}, chapter={self.chapter_number}, section={self.section_id})>"


class User(Base):
    """User account model with authentication credentials."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    # Relationships
    background = relationship("UserBackground", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, full_name={self.full_name})>"


class UserBackground(Base):
    """User questionnaire and background information."""
    __tablename__ = "user_backgrounds"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    software_background = Column(String(255), nullable=True)
    hardware_background = Column(String(255), nullable=True)
    ros_experience = Column(String(255), nullable=True)
    python_level = Column(String(255), nullable=True)
    learning_goal = Column(String(500), nullable=True)
    available_hardware = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="background")

    def __repr__(self):
        return f"<UserBackground(user_id={self.user_id}, python_level={self.python_level})>"
