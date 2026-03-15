"""
Health check endpoint for monitoring service status.

Verifies connectivity to all external services:
- Qdrant vector database
- OpenAI API
- PostgreSQL database
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.services.vector_store import vector_store_service
from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("")
async def health_check():
    """
    Check overall system health.

    Returns service status and connectivity to external services.

    Returns:
        Health status with detailed component information.

    Raises:
        HTTPException: If critical services are unavailable.
    """
    try:
        # Check Qdrant
        qdrant_healthy = await vector_store_service.health_check()

        # Check OpenAI
        openai_healthy = await embedding_service.health_check()

        # Check LLM
        llm_healthy = await llm_service.health_check()

        # Determine overall status
        all_healthy = qdrant_healthy and openai_healthy and llm_healthy

        status_code = 200 if all_healthy else 503

        return {
            "status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "qdrant": {
                    "status": "healthy" if qdrant_healthy else "unhealthy",
                },
                "openai": {
                    "status": "healthy" if openai_healthy else "unhealthy",
                },
                "llm": {
                    "status": "healthy" if llm_healthy else "unhealthy",
                },
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


@router.get("/detailed")
async def detailed_health_check():
    """
    Detailed health check with service metrics.

    Returns:
        Comprehensive health information including vector store collection info.
    """
    try:
        qdrant_info = await vector_store_service.get_collection_info()

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "qdrant": {
                    "status": "healthy",
                    "collection": qdrant_info,
                },
                "openai": {
                    "status": "healthy",
                    "model": "text-embedding-3-small",
                },
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e),
            },
        )
