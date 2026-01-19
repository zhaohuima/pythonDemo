"""
RAG Retriever
Main interface for document ingestion and retrieval with citation support.
"""

import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path

from .document_loader import PDFLoader
from .text_chunker import TextChunker
from .embeddings import EmbeddingModel
from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Main RAG interface for document retrieval with citation support."""

    def __init__(
        self,
        documents_dir: str = "knowledge_base/documents",
        persist_directory: str = "vector_db/chroma_db",
        collection_name: str = "product_knowledge",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 150
    ):
        """
        Initialize the RAG retriever.

        Args:
            documents_dir: Directory containing PDF documents
            persist_directory: Directory for vector database storage
            collection_name: Name of the vector store collection
            embedding_model: Name of the sentence-transformers model
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.documents_dir = documents_dir
        self.persist_directory = persist_directory

        # Initialize components
        self.loader = PDFLoader(documents_dir)
        self.chunker = TextChunker(chunk_size, chunk_overlap)
        self.embeddings = EmbeddingModel(embedding_model)
        self.vector_store = VectorStore(persist_directory, collection_name)

        logger.info("RAG Retriever initialized")

    def ingest_documents(self, clear_existing: bool = True) -> Dict:
        """
        Load, chunk, embed, and store all PDF documents.

        Args:
            clear_existing: Whether to clear existing documents before ingestion

        Returns:
            Dictionary with ingestion statistics
        """
        logger.info("Starting document ingestion...")

        # Clear existing documents if requested
        if clear_existing:
            try:
                self.vector_store.clear_collection()
            except Exception as e:
                logger.warning(f"Could not clear collection: {e}")

        # Load all PDFs
        documents = self.loader.load_all_documents()
        if not documents:
            return {
                "status": "warning",
                "message": "No documents found to ingest",
                "documents_processed": 0,
                "chunks_created": 0
            }

        # Get unique document names
        doc_names = set(doc["metadata"]["source"] for doc in documents)

        # Chunk documents
        chunked_docs = self.chunker.chunk_documents(documents)
        if not chunked_docs:
            return {
                "status": "error",
                "message": "Failed to chunk documents",
                "documents_processed": len(doc_names),
                "chunks_created": 0
            }

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(chunked_docs)} chunks...")
        texts = [doc["content"] for doc in chunked_docs]
        embeddings = self.embeddings.embed_texts(texts)

        # Store in vector database
        self.vector_store.add_documents(chunked_docs, embeddings)

        result = {
            "status": "success",
            "message": "Documents ingested successfully",
            "documents_processed": len(doc_names),
            "pages_processed": len(documents),
            "chunks_created": len(chunked_docs),
            "document_names": list(doc_names)
        }

        logger.info(f"Ingestion complete: {result}")
        return result

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant document chunks for a query.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant documents with metadata and scores
        """
        if not query:
            return []

        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)

        # Query vector store
        results = self.vector_store.query(query_embedding, top_k)

        logger.info(f"Retrieved {len(results)} documents for query: {query[:50]}...")
        return results

    def format_context_with_citations(
        self,
        documents: List[Dict]
    ) -> Tuple[str, List[Dict]]:
        """
        Format retrieved documents as context with citations.

        Args:
            documents: List of retrieved documents

        Returns:
            Tuple of (formatted context string, list of citations)
        """
        if not documents:
            return "", []

        context_parts = []
        citations = []

        for i, doc in enumerate(documents, start=1):
            metadata = doc.get("metadata", {})
            content = doc.get("content", "")
            score = doc.get("score", 0)

            # Extract citation info
            source = metadata.get("source", "Unknown Document")
            section = metadata.get("section", "Unknown Section")
            page = metadata.get("page", "?")

            # Build citation
            citation = {
                "id": i,
                "document": source,
                "section": section,
                "page": page,
                "relevance_score": round(score, 3)
            }
            citations.append(citation)

            # Build context entry
            context_entry = f'[{i}] From "{source}", {section} (Page {page}):\n"{content[:500]}{"..." if len(content) > 500 else ""}"'
            context_parts.append(context_entry)

        context_str = "\n\n".join(context_parts)
        return context_str, citations

    def get_status(self) -> Dict:
        """
        Get RAG system status.

        Returns:
            Dictionary with system status information
        """
        stats = self.vector_store.get_stats()
        doc_list = self.loader.get_document_list()

        return {
            "enabled": True,
            "documents_in_knowledge_base": len(doc_list),
            "chunks_in_vector_store": stats["document_count"],
            "persist_directory": stats["persist_directory"],
            "documents": doc_list
        }

    def add_document(self, file_path: str) -> Dict:
        """
        Add a single document to the knowledge base.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary with ingestion result
        """
        # Load the document
        documents = self.loader.load_pdf(file_path)
        if not documents:
            return {
                "status": "error",
                "message": f"Failed to load document: {file_path}"
            }

        # Chunk documents
        chunked_docs = self.chunker.chunk_documents(documents)

        # Generate embeddings
        texts = [doc["content"] for doc in chunked_docs]
        embeddings = self.embeddings.embed_texts(texts)

        # Store in vector database
        self.vector_store.add_documents(chunked_docs, embeddings)

        return {
            "status": "success",
            "message": f"Document added successfully",
            "pages_processed": len(documents),
            "chunks_created": len(chunked_docs)
        }

    def rebuild_index(self) -> Dict:
        """
        Rebuild the entire vector index from documents.

        Returns:
            Dictionary with rebuild result
        """
        return self.ingest_documents(clear_existing=True)
