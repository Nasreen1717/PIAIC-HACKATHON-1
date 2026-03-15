"""
Pydantic schemas for chat API requests and responses.

Defines request/response models with validation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """Citation reference for textbook source."""

    chapter_number: int
    section_id: str
    section_title: str
    source_text: Optional[str] = None
    similarity_score: Optional[float] = None
    chunk_id: Optional[str] = None
    url: Optional[str] = None  # Docusaurus URL path for navigation

    class Config:
        json_schema_extra = {
            "example": {
                "chapter_number": 2,
                "section_id": "2.1",
                "section_title": "Locomotion Basics",
                "similarity_score": 0.95,
                "url": "/docs/module-1/chapter-2#2-1"
            }
        }


class ChatRequest(BaseModel):
    """Chat API request."""

    question: str = Field(..., description="User's question", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="Session ID for conversation persistence")
    selected_text: Optional[str] = Field(None, description="Text selected from textbook")
    chapter_path: Optional[str] = Field(None, description="Path to the chapter containing selected text")
    section_id: Optional[str] = Field(None, description="Section ID for selected text")
    section_title: Optional[str] = Field(None, description="Title of section containing selected text")
    context_before: Optional[str] = Field(None, description="Context before selected text")
    context_after: Optional[str] = Field(None, description="Context after selected text")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is bipedal locomotion?",
                "session_id": "session_12345",
                "selected_text": None,
            }
        }


class ChatResponse(BaseModel):
    """Chat API response."""

    answer: str = Field(..., description="Generated answer")
    citations: List[Citation] = Field(default_factory=list, description="List of citations")
    confidence_score: Optional[float] = Field(None, description="Confidence score (0-1)")
    response_time_ms: Optional[float] = Field(None, description="Response generation time in milliseconds")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Bipedal locomotion is the movement on two legs...",
                "citations": [
                    {
                        "chapter_number": 2,
                        "section_id": "2.3",
                        "section_title": "Bipedal Movement",
                    }
                ],
                "confidence_score": 0.92,
            }
        }


class ConversationSession(BaseModel):
    """Conversation session metadata."""

    session_id: str
    message_count: int
    created_at: str
    updated_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_123",
                "message_count": 5,
                "created_at": "2024-01-27T10:00:00Z",
                "updated_at": "2024-01-27T10:15:00Z",
            }
        }


class MessageHistory(BaseModel):
    """Historical message from conversation."""

    id: str
    role: str  # "user" or "assistant"
    content: str
    citations: Optional[List[Citation]] = None
    created_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg_123",
                "role": "user",
                "content": "What is bipedal locomotion?",
                "citations": None,
                "created_at": "2024-01-27T10:05:00Z",
            }
        }


class ConversationHistory(BaseModel):
    """Complete conversation history."""

    session: ConversationSession
    messages: List[MessageHistory]

    class Config:
        json_schema_extra = {
            "example": {
                "session": {
                    "session_id": "sess_123",
                    "message_count": 2,
                    "created_at": "2024-01-27T10:00:00Z",
                    "updated_at": "2024-01-27T10:05:00Z",
                },
                "messages": [
                    {
                        "id": "msg_1",
                        "role": "user",
                        "content": "What is bipedal locomotion?",
                        "created_at": "2024-01-27T10:01:00Z",
                    }
                ],
            }
        }
