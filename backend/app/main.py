"""
FastAPI application for RAG Chatbot serving the Physical AI textbook.

Provides endpoints for:
- Chat queries with vector search and LLM grounding
- Conversation history retrieval
- Health checks and metrics
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.middleware import TimingMiddleware, ErrorHandlingMiddleware
from app.api.v1 import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    print(f"🚀 Starting RAG Chatbot backend (environment: {settings.ENVIRONMENT})")

    # Initialize database tables
    try:
        from app.services.database import database_service
        await database_service.create_tables()
        print("✓ Database tables initialized")
    except Exception as e:
        print(f"⚠️  Could not initialize database tables: {str(e)}")

    # **T031**: Verify Qdrant has content before accepting requests
    try:
        from app.services.vector_store import vector_store_service

        # Initialize Qdrant collection
        await vector_store_service.initialize_collection()
        print("✓ Services initialized")

    except Exception as e:
        print(f"⚠️  Could not initialize services: {str(e)}")

    yield

    # Shutdown
    print("🛑 Shutting down RAG Chatbot backend")


app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval-Augmented Generation chatbot for Physical AI textbook",
    version="0.1.0",
    lifespan=lifespan,
)

# Add middleware (order matters - later middleware wraps earlier ones)
app.add_middleware(TimingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
from app.api.v1 import chat, debug, translate, personalize
from app.routes.auth import router as auth_router

app.include_router(health.router)
app.include_router(auth_router)
app.include_router(chat.router)
app.include_router(translate.router)
app.include_router(personalize.router)
app.include_router(debug.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Chatbot API",
        "version": "0.1.0",
        "status": "running",
    }
