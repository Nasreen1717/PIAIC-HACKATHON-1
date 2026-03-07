"""
Chat API endpoints for RAG chatbot.

Provides:
- POST /chat: Submit question and receive grounded response
- GET /chat/history/{session_id}: Retrieve conversation history
- POST /chat/sessions: Create new chat session
"""

import time
import logging
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
import json

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    Citation,
    ConversationHistory,
    ConversationSession,
    MessageHistory,
)
from app.services.llm_service import llm_service
from app.services.vector_store import vector_store_service
from app.services.embedding_service import embedding_service
from app.services.database import database_service
from app.utils.citation_formatter import CitationFormatter
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# In-memory cache for active conversations (in production, use Redis)
active_conversations: dict = {}


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
) -> ChatResponse:
    """
    Submit a question and receive a grounded response with citations.

    **T022**: Create chat endpoint for question submission
    **T023**: Implement query embedding
    **T024**: Implement vector search (top-5 relevant chunks)
    **T025**: Implement LLM grounding with GPT-4
    **T026**: Implement response validation
    **T027**: Implement citation formatting
    **T029**: Implement out-of-scope handling
    **T028**: Store conversation to Postgres (async, non-blocking)

    Args:
        request: ChatRequest with question and optional session/context
        background_tasks: FastAPI background tasks for async operations

    Returns:
        ChatResponse with answer, citations, and confidence score

    Raises:
        HTTPException: 400 for invalid input, 408 for timeout, 503 for service unavailable
    """
    start_time = time.time()

    try:
        # Validate input
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        if len(request.question) > 2000:
            raise HTTPException(status_code=400, detail="Question too long (max 2000 chars)")

        # Generate session ID if not provided
        session_id = request.session_id or f"session_{uuid4().hex[:12]}"

        logger.info(f"Processing question for session {session_id}: {request.question[:50]}...")

        # **T023**: Embed the question
        try:
            question_embedding = await embedding_service.embed_text(request.question)
        except Exception as e:
            logger.error(f"Embedding failed: {str(e)}")
            raise HTTPException(status_code=503, detail="Embedding service unavailable")

        # **T034**: Check if selected_text provided (bypass vector search for text selection)
        retrieved_chunks = []
        search_latency_ms = 0

        if request.selected_text:
            # Text selection path: use selected text directly as context
            logger.info(f"Using selected text context (bypass vector search)")
            retrieved_chunks = [
                {
                    "id": f"selection_{uuid4().hex[:8]}",
                    "payload": {
                        "content": request.selected_text,
                        "chapter_number": _extract_chapter_from_path(request.chapter_path) if request.chapter_path else 0,
                        "section_id": request.section_id or "selected",
                        "section_title": request.section_title or "Selected Text",
                        "content_type": "text",
                        "chunk_index": 0,
                    },
                    "score": 1.0,  # Perfect match for selected text
                }
            ]
        else:
            # **T024**: Vector search for top-5 relevant chunks
            try:
                search_start = time.time()
                retrieved_chunks = await vector_store_service.search(
                    vector=question_embedding,
                    limit=5,
                    score_threshold=0.4,  # Aggressive threshold for better recall
                )
                search_latency_ms = (time.time() - search_start) * 1000

                # Detailed logging for debugging
                logger.info(f"Vector search: question='{request.question[:50]}...' returned {len(retrieved_chunks)} chunks")
                for i, chunk in enumerate(retrieved_chunks[:3]):
                    payload = chunk.get('payload', {})
                    logger.debug(f"  [{i+1}] score={chunk.get('score', 0):.4f}, chapter={payload.get('chapter_number')}, section={payload.get('section_id')}")

                if not retrieved_chunks:
                    logger.warning(f"Vector search returned 0 results for: {request.question[:80]}")

            except Exception as e:
                logger.error(f"Vector search failed: {str(e)}")
                raise HTTPException(status_code=503, detail="Vector search unavailable")

        # **T029**: Handle out-of-scope questions (no relevant chunks)
        # **T029**: Handle out-of-scope questions with fallback search
        # First pass: strict matching with lowered threshold
        if not retrieved_chunks or (retrieved_chunks and retrieved_chunks[0].get("score", 0) < 0.35):
            # Fallback: try broader search with even lower threshold
            logger.info(f"First search low confidence, attempting fallback search")
            try:
                fallback_chunks = await vector_store_service.search(
                    vector=question_embedding,
                    limit=5,
                    score_threshold=0.2,  # Very broad fallback
                )
                if fallback_chunks and fallback_chunks[0].get("score", 0) >= 0.25:
                    retrieved_chunks = fallback_chunks
                    logger.info(f"Fallback search succeeded with score {fallback_chunks[0].get('score', 0):.4f}")
                else:
                    logger.warning(f"Out-of-scope question: {request.question}")
                    return ChatResponse(
                        answer="I cannot answer this question based on the available textbook material. Please try rewording your question or consult the relevant textbook chapter directly.",
                        citations=[],
                        confidence_score=0.0,
                        response_time_ms=time.time() - start_time,
                    )
            except Exception as e:
                logger.warning(f"Fallback search failed: {str(e)}")
                return ChatResponse(
                    answer="I cannot answer this question based on the available textbook material. Please try rewording your question or consult the relevant textbook chapter directly.",
                    citations=[],
                    confidence_score=0.0,
                    response_time_ms=time.time() - start_time,
                )

        # **T025**: Call LLM with grounding (system prompt enforces constraints)
        # **T055**: Load conversation history for multi-turn context
        try:
            conversation_history = None
            if request.session_id:
                try:
                    history_data = await database_service.get_conversation_history(request.session_id)
                    if history_data and history_data.get("messages"):
                        # Extract only role and content for LLM context (exclude current question)
                        conversation_history = [
                            {
                                "role": msg["role"],
                                "content": msg["content"],
                            }
                            for msg in history_data["messages"]
                            # Don't include the current question again (it will be added by generate_grounded_response)
                        ]
                        if conversation_history:
                            logger.info(f"Loaded {len(conversation_history)} messages from conversation history")
                except Exception as e:
                    logger.warning(f"Failed to load conversation history: {str(e)}")
                    # Continue without history if retrieval fails
                    conversation_history = None

            llm_start = time.time()
            answer_text, citations_data = await llm_service.generate_grounded_response(
                question=request.question,
                retrieved_chunks=retrieved_chunks,
                conversation_history=conversation_history,
            )
            llm_latency_ms = (time.time() - llm_start) * 1000
            logger.info(f"LLM generation completed (latency: {llm_latency_ms:.1f}ms)")

        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise HTTPException(status_code=503, detail="LLM service unavailable")

        # **T026**: Validate response relevance and confidence
        # Check if answer contains "cannot answer" or similar refusals
        refusal_indicators = [
            "cannot answer",
            "not available",
            "outside the scope",
            "not covered",
            "cannot be answered",
        ]
        is_refusing = any(indicator in answer_text.lower() for indicator in refusal_indicators)

        confidence_score = 0.0 if is_refusing else min(0.95, (sum(c.get("score", 0) for c in retrieved_chunks) / len(retrieved_chunks)) if retrieved_chunks else 0.0)

        # **T027**: Format citations with validation
        citations = []
        for citation_data in citations_data:
            try:
                chapter = citation_data.get("chapter_number")
                section_id = citation_data.get("section_id")
                section_title = citation_data.get("section_title")

                # Generate URL
                url = CitationFormatter.generate_docusaurus_url(chapter, section_id)

                ieee_citation = CitationFormatter.format_ieee_citation(
                    chapter_number=chapter,
                    section_id=section_id,
                    section_title=section_title,
                )

                citation = Citation(
                    chapter_number=chapter,
                    section_id=section_id,
                    section_title=section_title,
                    similarity_score=citation_data.get("score"),
                    chunk_id=citation_data.get("chunk_id"),
                    url=url  # Include URL in citation response
                )
                citations.append(citation)

                logger.debug(f"Citation generated: {ieee_citation} → {url}")

            except Exception as e:
                logger.warning(f"Citation formatting error for {citation_data}: {str(e)}")

        response_time_ms = (time.time() - start_time) * 1000

        # **T030**: Log performance metrics (via middleware would be better)
        logger.info(f"Chat completed - Search: {search_latency_ms:.1f}ms, LLM: {llm_latency_ms:.1f}ms, Total: {response_time_ms:.1f}ms")

        # **T028**: Store conversation to Postgres (async, non-blocking)
        background_tasks.add_task(
            _store_conversation,
            session_id=session_id,
            question=request.question,
            answer=answer_text,
            citations=citations_data,
        )

        return ChatResponse(
            answer=answer_text,
            citations=citations,
            confidence_score=confidence_score,
            response_time_ms=response_time_ms,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/stream")
async def stream_chat(request: ChatRequest):
    """
    **T098**: Streaming chat endpoint for real-time token delivery.

    Uses Server-Sent Events (SSE) to stream tokens as they arrive from LLM.
    Enables "typewriter effect" for better UX.

    Returns:
        StreamingResponse with SSE events
    """
    async def event_generator():
        try:
            # Embed question
            yield f"data: {json.dumps({'type': 'thinking', 'delta': 'Processing your question...'})}\n\n"

            question_embedding = await embedding_service.embed_text(request.question)

            # Check if selected_text provided (replicate non-streaming logic from lines 96-112)
            logger.info(f"[STREAM] Request received - question: {request.question[:50]}...")
            logger.info(f"[STREAM] selected_text provided: {bool(request.selected_text)}")

            if request.selected_text:
                # Text selection path: bypass vector search, use selected text directly
                logger.info(f"[STREAM] Using selected text context (bypass vector search)")
                logger.info(f"[STREAM] selected_text length: {len(request.selected_text)}, chapter: {request.chapter_path}, section: {request.section_title}")
                yield f"data: {json.dumps({'type': 'selection_mode', 'delta': 'Using your selected text...'})}\n\n"

                retrieved_chunks = [
                    {
                        "id": f"selection_{uuid4().hex[:8]}",
                        "payload": {
                            "content": request.selected_text,
                            "chapter_number": _extract_chapter_from_path(request.chapter_path) if request.chapter_path else 0,
                            "section_id": request.section_id or "selected",
                            "section_title": request.section_title or "Selected Text",
                            "content_type": "text",
                            "chunk_index": 0,
                        },
                        "score": 1.0,  # Perfect match for selected text
                    }
                ]
            else:
                # Vector search (existing flow for general questions)
                yield f"data: {json.dumps({'type': 'retrieving', 'delta': 'Searching textbook...'})}\n\n"

                retrieved_chunks = await vector_store_service.search(
                    vector=question_embedding,
                    limit=5,
                    score_threshold=0.6,
                )

                yield f"data: {json.dumps({'type': 'retrieval', 'chunks': [{'chapter': c['payload']['chapter_number'], 'section': c['payload']['section_title']} for c in retrieved_chunks[:3]]})}\n\n"

            # LLM generation (stream tokens)
            yield f"data: {json.dumps({'type': 'response_start', 'timestamp': datetime.now().isoformat()})}\n\n"

            answer_text, citations_data = await llm_service.generate_grounded_response(
                question=request.question,
                retrieved_chunks=retrieved_chunks,
            )

            # Stream answer tokens
            for token in answer_text.split(" "):
                yield f"data: {json.dumps({'type': 'text_delta', 'delta': token + ' '})}\n\n"

            # Send citations
            for citation_data in citations_data:
                yield f"data: {json.dumps({'type': 'citation', 'ieee': CitationFormatter.format_ieee_citation(
                    chapter_number=citation_data.get("chapter_number"),
                    section_id=citation_data.get("section_id"),
                    section_title=citation_data.get("section_title"),
                )})}\n\n"

            yield f"data: {json.dumps({'type': 'response_end', 'confidence': min(0.95, max(c.get('score', 0) for c in retrieved_chunks))})}Confidence\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/history/{session_id}", response_model=ConversationHistory)
async def get_conversation_history(session_id: str) -> ConversationHistory:
    """
    **T050**: Retrieve conversation history for a session.

    Args:
        session_id: Session identifier

    Returns:
        ConversationHistory with all messages and metadata

    Raises:
        HTTPException: 404 if session not found
    """
    try:
        conversation = await database_service.get_conversation_history(session_id)

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return conversation

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")


@router.post("/sessions")
async def create_session():
    """
    **T051**: Create a new chat session.

    Returns:
        ConversationSession with session metadata

    Example response:
        {
            "session_id": "session_abc123",
            "message_count": 0,
            "created_at": "2024-01-27T10:00:00Z",
            "updated_at": "2024-01-27T10:00:00Z"
        }
    """
    try:
        session_id = f"session_{uuid4().hex[:12]}"
        now = datetime.now().isoformat()

        session = ConversationSession(
            session_id=session_id,
            message_count=0,
            created_at=now,
            updated_at=now,
        )

        # Store in database
        await database_service.create_session(session_id, now)

        logger.info(f"Created session {session_id}")

        return session

    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create session")


# Helper functions


async def _store_conversation(
    session_id: str,
    question: str,
    answer: str,
    citations: List[dict],
) -> None:
    """
    **T028**: Store conversation message to Postgres (async, non-blocking).

    Args:
        session_id: Session identifier
        question: User question
        answer: Assistant answer
        citations: List of citation data

    Logs errors but doesn't raise (non-blocking operation).
    """
    try:
        await database_service.store_message(
            session_id=session_id,
            role="user",
            content=question,
        )

        await database_service.store_message(
            session_id=session_id,
            role="assistant",
            content=answer,
            citations=citations,
        )

        logger.info(f"Stored conversation for session {session_id}")

    except Exception as e:
        logger.warning(f"Failed to store conversation: {str(e)}")
        # Don't raise - this is a non-blocking operation


def _extract_chapter_from_path(chapter_path: Optional[str]) -> int:
    """
    Extract chapter number from chapter path.

    Examples:
        "module-3/chapter-8" -> 8
        "chapter-5" -> 5

    Args:
        chapter_path: Path like "module-3/chapter-8"

    Returns:
        Chapter number as integer
    """
    if not chapter_path:
        return 0

    try:
        # Extract chapter number from path
        import re
        match = re.search(r"chapter-(\d+)", chapter_path)
        if match:
            return int(match.group(1))
    except Exception:
        pass

    return 0
