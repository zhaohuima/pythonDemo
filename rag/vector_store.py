"""
Vector Store using ChromaDB
Manages document storage and retrieval with persistent storage.
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB vector store for document storage and retrieval."""

    def __init__(
        self,
        persist_directory: str = "vector_db/chroma_db",
        collection_name: str = "product_knowledge"
    ):
        """
        Initialize the vector store.

        Args:
            persist_directory: Directory for persistent storage
            collection_name: Name of the ChromaDB collection
        """
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self._client = None
        self._collection = None

    def _init_client(self):
        """Initialize ChromaDB client and collection."""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings

                # Ensure directory exists
                self.persist_directory.mkdir(parents=True, exist_ok=True)

                # Initialize persistent client
                self._client = chromadb.PersistentClient(
                    path=str(self.persist_directory),
                    settings=Settings(anonymized_telemetry=False)
                )

                # Get or create collection
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )

                logger.info(f"ChromaDB initialized at {self.persist_directory}")
                logger.info(f"Collection '{self.collection_name}' has {self._collection.count()} documents")

            except ImportError:
                logger.error("chromadb not installed. Run: pip install chromadb")
                raise
            except Exception as e:
                logger.error(f"Error initializing ChromaDB: {e}")
                raise

    def add_documents(
        self,
        documents: List[Dict],
        embeddings: List[List[float]],
        ids: Optional[List[str]] = None
    ) -> int:
        """
        Add documents with embeddings to the vector store.

        Args:
            documents: List of documents with content and metadata
            embeddings: List of embedding vectors
            ids: Optional list of document IDs

        Returns:
            Number of documents added
        """
        self._init_client()

        if not documents or not embeddings:
            return 0

        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")

        # Generate IDs if not provided
        if ids is None:
            existing_count = self._collection.count()
            ids = [f"doc_{existing_count + i}" for i in range(len(documents))]

        # Prepare data for ChromaDB
        contents = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        # Convert metadata values to strings (ChromaDB requirement)
        for metadata in metadatas:
            for key, value in metadata.items():
                if not isinstance(value, (str, int, float, bool)):
                    metadata[key] = str(value)

        try:
            self._collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas
            )
            logger.info(f"Added {len(documents)} documents to vector store")
            return len(documents)
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query the vector store for similar documents.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            where: Optional filter conditions

        Returns:
            List of matching documents with scores
        """
        self._init_client()

        if self._collection.count() == 0:
            logger.warning("Vector store is empty")
            return []

        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self._collection.count()),
                where=where,
                include=["documents", "metadatas", "distances"]
            )

            # Format results
            documents = []
            if results and results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    # Convert distance to similarity score (cosine distance to similarity)
                    distance = results["distances"][0][i] if results["distances"] else 0
                    score = 1 - distance  # Convert distance to similarity

                    documents.append({
                        "id": doc_id,
                        "content": results["documents"][0][i] if results["documents"] else "",
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "score": score
                    })

            return documents

        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return []

    def delete_collection(self):
        """Delete the entire collection."""
        self._init_client()
        try:
            self._client.delete_collection(self.collection_name)
            self._collection = None
            logger.info(f"Deleted collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise

    def clear_collection(self):
        """Clear all documents from the collection."""
        self._init_client()
        try:
            # Delete and recreate collection
            self._client.delete_collection(self.collection_name)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Cleared collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise

    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store.

        Returns:
            Dictionary with collection statistics
        """
        self._init_client()
        return {
            "collection_name": self.collection_name,
            "document_count": self._collection.count(),
            "persist_directory": str(self.persist_directory)
        }
