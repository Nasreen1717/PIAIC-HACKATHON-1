"""
Embedding service for OpenAI text-embedding-3-small API.

Handles vector embedding generation for text chunks and queries.
"""

from typing import List
from openai import AsyncOpenAI
from app.core.config import settings


class EmbeddingService:
    """Manages text embedding generation via OpenAI API."""

    def __init__(self):
        """Initialize OpenAI async client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.

        Args:
            text: Text to embed.

        Returns:
            Vector embedding (1536-dimensional for text-embedding-3-small).

        Raises:
            Exception: If embedding generation fails.
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Failed to generate embedding: {str(e)}")

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a batch.

        Args:
            texts: List of texts to embed.

        Returns:
            List of vector embeddings.

        Raises:
            Exception: If batch embedding fails.
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
            raise Exception(f"Failed to generate batch embeddings: {str(e)}")

    async def health_check(self) -> bool:
        """
        Check if OpenAI API is accessible.

        Returns:
            True if API is reachable, False otherwise.
        """
        try:
            await self.embed_text("health check")
            return True
        except Exception:
            return False


# Global instance
embedding_service = EmbeddingService()
