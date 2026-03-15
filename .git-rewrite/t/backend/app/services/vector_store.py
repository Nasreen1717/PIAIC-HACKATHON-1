"""
Vector store service for Qdrant integration.

Manages Qdrant client, collection initialization, and vector search operations.
"""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.core.config import settings


class VectorStoreService:
    """Manages Qdrant vector database operations."""

    def __init__(self):
        """Initialize Qdrant service (deferred client init)."""
        self._client: Optional[QdrantClient] = None
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    @property
    def client(self):
        """Get or initialize Qdrant client (lazy initialization)."""
        if self._client is None:
            try:
                self._client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=10.0,
                )
            except Exception as e:
                raise Exception(f"Failed to connect to Qdrant: {str(e)}")
        return self._client

    async def initialize_collection(self, vector_size: int = 1536):
        """
        Initialize Qdrant collection with proper configuration.

        Args:
            vector_size: Dimension of embedding vectors (1536 for text-embedding-3-small).

        Raises:
            Exception: If collection creation fails.
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                )
                print(f"✅ Created Qdrant collection: {self.collection_name}")
            else:
                print(f"📦 Collection already exists: {self.collection_name}")
        except Exception as e:
            raise Exception(f"Failed to initialize Qdrant collection: {str(e)}")

    async def search(
        self,
        vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the collection.

        Args:
            vector: Query embedding vector.
            limit: Maximum number of results to return.
            score_threshold: Minimum similarity score to include result.

        Returns:
            List of similar chunks with metadata and scores.
        """
        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=vector,
                limit=limit,
                score_threshold=score_threshold,
            )

            # Convert results to dict format
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                }
                for result in results.points
            ]
        except Exception as e:
            raise Exception(f"Vector search failed: {str(e)}")

    async def upsert_points(self, points: List[PointStruct]):
        """
        Insert or update points in the collection.

        Args:
            points: List of PointStruct objects to upsert.

        Raises:
            Exception: If upsert operation fails.
        """
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            print(f"✅ Upserted {len(points)} points to {self.collection_name}")
        except Exception as e:
            raise Exception(f"Failed to upsert points: {str(e)}")

    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.

        Returns:
            Collection metadata including point count, vector size, etc.
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.points_count,
                "vector_size": info.config.params.vectors.size,
            }
        except Exception as e:
            raise Exception(f"Failed to get collection info: {str(e)}")

    async def health_check(self) -> bool:
        """
        Check if Qdrant is accessible.

        Returns:
            True if healthy, False otherwise.
        """
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False


# Global instance
vector_store_service = VectorStoreService()
