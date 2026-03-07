"""
Main ingestion script orchestrating content parsing, chunking, and embedding.

Coordinates the full pipeline from raw textbook files to embedded vectors in Qdrant.
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from content_parser import parse_textbook
from chunking_strategy import chunk_textbook
from embedding_pipeline import embed_and_upload
from app.services.vector_store import vector_store_service
from app.core.config import settings


async def ingest_textbook():
    """
    Main ingestion workflow.

    Steps:
    1. Parse markdown/MDX files
    2. Extract sections and chapters
    3. Chunk content semantically
    4. Generate embeddings
    5. Upload to Qdrant
    """
    try:
        print("=" * 60)
        print("📚 RAG Chatbot Content Ingestion Pipeline")
        print("=" * 60)

        # Step 1: Parse
        print("\n📖 Step 1: Parsing textbook chapters...")
        chapters = parse_textbook()

        if not chapters:
            print("❌ No chapters found. Check textbook path.")
            return False

        # Step 2: Chunk
        print("\n✂️ Step 2: Chunking content semantically...")
        chunks = chunk_textbook(chapters, target_tokens=300, overlap_tokens=100)

        if not chunks:
            print("❌ No chunks created. Check content format.")
            return False

        # Step 3: Initialize Qdrant collection
        print("\n🔮 Step 3: Initializing Qdrant collection...")
        await vector_store_service.initialize_collection(vector_size=1536)

        # Step 4: Embed and Upload
        print("\n⚡ Step 4: Generating embeddings and uploading to Qdrant...")
        stats = await embed_and_upload(chunks, settings.OPENAI_API_KEY, vector_store_service)

        print(f"\n✅ Ingestion Complete!")
        print(f"   Chunks processed: {stats['chunks_processed']}")
        print(f"   Points uploaded: {stats['points_uploaded']}")
        print(f"   Vector dimension: {stats['vector_dimension']}")

        # Verify
        print("\n🔍 Step 5: Verifying Qdrant collection...")
        collection_info = await vector_store_service.get_collection_info()
        print(f"   Collection: {collection_info['name']}")
        print(f"   Total vectors: {collection_info['vectors_count']}")
        print(f"   Vector size: {collection_info['vector_size']}")

        print("\n" + "=" * 60)
        print("🚀 RAG Chatbot is ready to serve!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Ingestion failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(ingest_textbook())
    sys.exit(0 if success else 1)
