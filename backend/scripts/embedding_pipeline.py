"""
Embedding pipeline for generating and storing vectors.

Batch processes chunks through OpenAI embeddings and uploads to Qdrant.
"""

import asyncio
import uuid
from typing import List, Dict, Any
from qdrant_client.models import PointStruct
from openai import AsyncOpenAI


class EmbeddingPipeline:
    """Manages batch embedding generation and Qdrant upload."""

    def __init__(self, openai_api_key: str, batch_size: int = 50):
        """
        Initialize embedding pipeline.

        Args:
            openai_api_key: OpenAI API key.
            batch_size: Number of texts to embed per API call.
        """
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.batch_size = batch_size
        self.model = "text-embedding-3-small"

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
            # Sort by index to maintain order
            embeddings = sorted(response.data, key=lambda x: x.index)
            return [emb.embedding for emb in embeddings]
        except Exception as e:
            raise Exception(f"Embedding failed: {str(e)}")

    async def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for all chunks.

        Args:
            chunks: List of chunks with content.

        Returns:
            Chunks enriched with embeddings.
        """
        embedded_chunks = []

        # Process in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i : i + self.batch_size]
            texts = [chunk["content"] for chunk in batch]

            print(f"🔄 Embedding batch {i // self.batch_size + 1}/{(len(chunks) + self.batch_size - 1) // self.batch_size}")

            embeddings = await self.embed_batch(texts)

            for chunk, embedding in zip(batch, embeddings):
                chunk["embedding"] = embedding
                embedded_chunks.append(chunk)

        return embedded_chunks

    def create_qdrant_points(self, embedded_chunks: List[Dict[str, Any]]) -> List[PointStruct]:
        """
        Convert embedded chunks to Qdrant PointStruct format.

        Args:
            embedded_chunks: Chunks with embeddings.

        Returns:
            List of Qdrant PointStruct objects.
        """
        points = []

        for chunk in embedded_chunks:
            point = PointStruct(
                id=str(uuid.uuid4()),  # Generate unique ID
                vector=chunk["embedding"],
                payload={
                    "chunk_id": chunk["chunk_id"],
                    "chapter_number": chunk["chapter_number"],
                    "section_id": chunk["section_id"],
                    "section_title": chunk["section_title"],
                    "content": chunk["content"],
                    "token_count": chunk["token_count"],
                },
            )
            points.append(point)

        return points


async def embed_and_upload(
    chunks: List[Dict[str, Any]],
    openai_api_key: str,
    vector_store_service,
) -> Dict[str, Any]:
    """
    Embed chunks and upload to Qdrant.

    Args:
        chunks: List of chunks to embed.
        openai_api_key: OpenAI API key.
        vector_store_service: VectorStoreService instance.

    Returns:
        Statistics about embedding process.
    """
    pipeline = EmbeddingPipeline(openai_api_key)

    print(f"🚀 Starting embedding pipeline for {len(chunks)} chunks...")

    # Embed chunks
    embedded_chunks = await pipeline.embed_chunks(chunks)

    # Create Qdrant points
    points = pipeline.create_qdrant_points(embedded_chunks)

    # Upload to Qdrant
    await vector_store_service.upsert_points(points)

    return {
        "chunks_processed": len(embedded_chunks),
        "points_uploaded": len(points),
        "vector_dimension": len(embedded_chunks[0]["embedding"]) if embedded_chunks else 0,
    }


if __name__ == "__main__":
    import os
    from content_parser import parse_textbook
    from chunking_strategy import chunk_textbook

    # Parse and chunk
    chapters = parse_textbook()
    chunks = chunk_textbook(chapters)

    # Mock embedding (requires real OpenAI key to run)
    print(f"\n✅ Ready to embed {len(chunks)} chunks")
    print("   Run this with real OpenAI key and vector store connection")
