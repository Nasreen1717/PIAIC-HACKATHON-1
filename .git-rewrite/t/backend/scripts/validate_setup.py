"""
Setup validation script to verify all services are working.

Checks:
- FastAPI server
- Qdrant connectivity
- OpenAI API
- PostgreSQL database
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store import vector_store_service
from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service
from app.services.database import db_service
from app.core.config import settings


async def validate_setup():
    """
    Validate all external service connections.

    Returns:
        True if all services are healthy, False otherwise.
    """
    print("=" * 60)
    print("🔍 RAG Chatbot Setup Validation")
    print("=" * 60)

    results = {}

    # Check Qdrant
    print("\n✓ Checking Qdrant Vector Database...")
    try:
        health = await vector_store_service.health_check()
        if health:
            results["qdrant"] = "✅ Healthy"
            print(f"  {results['qdrant']}")
        else:
            results["qdrant"] = "❌ Unhealthy"
            print(f"  {results['qdrant']}")
    except Exception as e:
        results["qdrant"] = f"❌ Error: {str(e)}"
        print(f"  {results['qdrant']}")

    # Check OpenAI Embeddings
    print("\n✓ Checking OpenAI Embeddings API...")
    try:
        health = await embedding_service.health_check()
        if health:
            results["embeddings"] = "✅ Healthy"
            print(f"  {results['embeddings']}")
        else:
            results["embeddings"] = "❌ Unhealthy"
            print(f"  {results['embeddings']}")
    except Exception as e:
        results["embeddings"] = f"❌ Error: {str(e)}"
        print(f"  {results['embeddings']}")

    # Check OpenAI LLM
    print("\n✓ Checking OpenAI GPT-4 API...")
    try:
        health = await llm_service.health_check()
        if health:
            results["llm"] = "✅ Healthy"
            print(f"  {results['llm']}")
        else:
            results["llm"] = "❌ Unhealthy"
            print(f"  {results['llm']}")
    except Exception as e:
        results["llm"] = f"❌ Error: {str(e)}"
        print(f"  {results['llm']}")

    # Check PostgreSQL
    print("\n✓ Checking PostgreSQL Database...")
    try:
        await db_service.create_tables()
        results["database"] = "✅ Healthy"
        print(f"  {results['database']}")
    except Exception as e:
        results["database"] = f"❌ Error: {str(e)}"
        print(f"  {results['database']}")
    finally:
        await db_service.close()

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    all_healthy = True
    for service, status in results.items():
        print(f"{service.upper():20} {status}")
        if "❌" in status or "Error" in status:
            all_healthy = False

    print("\n" + ("=" * 60))
    if all_healthy:
        print("✅ All services are healthy and ready!")
        print("=" * 60)
        return True
    else:
        print("❌ Some services are unhealthy. Check configurations.")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = asyncio.run(validate_setup())
    sys.exit(0 if success else 1)
