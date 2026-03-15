"""
SQLAlchemy models for RAG Chatbot.

Defines the data schema for:
- Conversations: User conversation sessions
- Messages: Individual chat messages (questions and answers)
- Citations: Sources referenced in answers
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Float, JSON
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
