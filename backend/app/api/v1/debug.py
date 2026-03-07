"""
Debug and diagnostic endpoints for RAG chatbot system.

Provides system health, vector store status, and citation URL validation.
"""

import asyncio
from fastapi import APIRouter, HTTPException
from app.services.vector_store import vector_store_service
from app.services.embedding_service import embedding_service
from app.utils.citation_url_mapping import get_all_chapters, get_all_references, validate_url

router = APIRouter(prefix="/api/v1/debug", tags=["debug"])


@router.get("/health")
async def health_check():
    """Check system health and service status."""
    try:
        # Check Qdrant
        qdrant_healthy = await vector_store_service.health_check()

        # Check OpenAI
        embedding_sample = await embedding_service.embed_text("test")
        openai_healthy = embedding_sample is not None and len(embedding_sample) > 0

        return {
            "status": "healthy" if (qdrant_healthy and openai_healthy) else "degraded",
            "services": {
                "qdrant": {"status": "healthy" if qdrant_healthy else "unhealthy"},
                "openai": {"status": "healthy" if openai_healthy else "unhealthy"}
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "services": {
                "qdrant": {"status": "error"},
                "openai": {"status": "error"}
            }
        }


@router.get("/vector-store-status")
async def vector_store_status():
    """Get vector store collection status."""
    try:
        client = vector_store_service.client
        collection = client.get_collection("physical_ai_textbook")

        return {
            "collection_name": collection.name,
            "points_count": collection.points_count,
            "vector_size": collection.config.params.vectors.size,
            "status": "healthy" if collection.points_count > 0 else "empty"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/citation-urls")
async def validate_citation_urls():
    """Validate all citation URLs in the mapping."""
    chapters = get_all_chapters()
    references = get_all_references()

    results = {
        "chapters": {},
        "references": {},
        "summary": {}
    }

    # Validate chapter URLs
    valid_chapters = 0
    for chapter_num, info in chapters.items():
        test_url = f"{info['url_base']}#test"
        is_valid = validate_url(test_url)
        results["chapters"][chapter_num] = {
            "url_base": info["url_base"],
            "valid": is_valid,
            "file": info["file"]
        }
        if is_valid:
            valid_chapters += 1

    # Validate reference URLs
    valid_refs = 0
    for module_num, info in references.items():
        test_url = f"{info['url_base']}#test"
        is_valid = validate_url(test_url)
        results["references"][module_num] = {
            "url_base": info["url_base"],
            "valid": is_valid,
            "file": info["file"],
            "type": info["type"]
        }
        if is_valid:
            valid_refs += 1

    results["summary"] = {
        "total_chapters": len(chapters),
        "valid_chapters": valid_chapters,
        "total_references": len(references),
        "valid_references": valid_refs,
        "all_valid": valid_chapters == len(chapters) and valid_refs == len(references)
    }

    return results


@router.post("/test-search")
async def test_vector_search(question: str):
    """Test vector search and return results with detailed debug info."""
    try:
        # Embed the question
        vector = await embedding_service.embed_text(question)

        # Try search with different thresholds
        results_04 = await vector_store_service.search(vector, limit=5, score_threshold=0.4)
        results_03 = await vector_store_service.search(vector, limit=5, score_threshold=0.3) if not results_04 else []
        results_02 = await vector_store_service.search(vector, limit=5, score_threshold=0.2) if not results_03 else []

        return {
            "question": question,
            "search_results": {
                "threshold_0_4": {
                    "count": len(results_04),
                    "chunks": [
                        {
                            "score": r.get("score"),
                            "chapter": r.get("payload", {}).get("chapter_number"),
                            "section_id": r.get("payload", {}).get("section_id"),
                            "section_title": r.get("payload", {}).get("section_title", "")[:50]
                        }
                        for r in results_04[:3]
                    ]
                },
                "threshold_0_3": {
                    "count": len(results_03),
                    "chunks": [
                        {
                            "score": r.get("score"),
                            "chapter": r.get("payload", {}).get("chapter_number"),
                            "section_id": r.get("payload", {}).get("section_id")
                        }
                        for r in results_03[:2]
                    ] if results_03 else []
                },
                "threshold_0_2": {
                    "count": len(results_02),
                    "chunks": [
                        {
                            "score": r.get("score"),
                            "chapter": r.get("payload", {}).get("chapter_number"),
                            "section_id": r.get("payload", {}).get("section_id")
                        }
                        for r in results_02[:2]
                    ] if results_02 else []
                }
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "question": question
        }
