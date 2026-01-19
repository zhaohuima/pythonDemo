"""
Embedding Model Wrapper
Uses sentence-transformers for generating text embeddings.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """Wrapper for sentence-transformers embedding model."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding model.

        Args:
            model_name: Name of the sentence-transformers model to use
        """
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        """Lazy load the model on first use."""
        if self._model is None:
            try:
                # 设置离线模式，避免网络超时问题
                # Set offline mode to avoid network timeout issues
                import os
                os.environ['HF_HUB_OFFLINE'] = '1'
                os.environ['TRANSFORMERS_OFFLINE'] = '1'

                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {self.model_name} (offline mode)")
                self._model = SentenceTransformer(self.model_name)
                logger.info("Embedding model loaded successfully")
            except ImportError:
                logger.error("sentence-transformers not installed. Run: pip install sentence-transformers")
                raise
            except Exception as e:
                logger.error(f"Error loading embedding model: {e}")
                raise

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing

        Returns:
            List of embedding vectors
        """
        self._load_model()

        if not texts:
            return []

        try:
            embeddings = self._model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=len(texts) > 100,
                convert_to_numpy=True
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.

        Args:
            query: Query text to embed

        Returns:
            Embedding vector
        """
        self._load_model()

        try:
            embedding = self._model.encode(query, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise

    @property
    def dimension(self) -> int:
        """Get the embedding dimension."""
        self._load_model()
        return self._model.get_sentence_embedding_dimension()
