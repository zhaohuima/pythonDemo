"""
Text Chunker for RAG
Splits documents into optimal chunks for embedding and retrieval.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class TextChunker:
    """Split documents into chunks while preserving metadata."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        """
        Initialize the text chunker.

        Args:
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Simple sentence splitting on common delimiters
        import re
        # Split on period, exclamation, question mark followed by space or newline
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs.

        Args:
            text: Text to split

        Returns:
            List of paragraphs
        """
        # Split on double newlines or multiple newlines
        paragraphs = text.split('\n\n')
        result = []
        for p in paragraphs:
            p = p.strip()
            if p:
                result.append(p)
        return result

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks of approximately chunk_size characters.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        paragraphs = self._split_into_paragraphs(text)

        current_chunk = ""

        for paragraph in paragraphs:
            # If paragraph itself is too long, split by sentences
            if len(paragraph) > self.chunk_size:
                sentences = self._split_into_sentences(paragraph)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) + 1 <= self.chunk_size:
                        current_chunk += (" " if current_chunk else "") + sentence
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        # If single sentence is too long, split by characters
                        if len(sentence) > self.chunk_size:
                            # Split long sentence into smaller pieces
                            for i in range(0, len(sentence), self.chunk_size - self.chunk_overlap):
                                chunk = sentence[i:i + self.chunk_size]
                                chunks.append(chunk)
                            current_chunk = ""
                        else:
                            current_chunk = sentence
            else:
                # Add paragraph to current chunk if it fits
                if len(current_chunk) + len(paragraph) + 2 <= self.chunk_size:
                    current_chunk += ("\n\n" if current_chunk else "") + paragraph
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = paragraph

        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk)

        # Add overlap between chunks
        if self.chunk_overlap > 0 and len(chunks) > 1:
            overlapped_chunks = []
            for i, chunk in enumerate(chunks):
                if i > 0:
                    # Add overlap from previous chunk
                    prev_chunk = chunks[i - 1]
                    overlap_text = prev_chunk[-self.chunk_overlap:] if len(prev_chunk) > self.chunk_overlap else prev_chunk
                    chunk = overlap_text + " " + chunk
                overlapped_chunks.append(chunk)
            chunks = overlapped_chunks

        return chunks

    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Split documents into chunks while preserving metadata.

        Args:
            documents: List of documents with content and metadata

        Returns:
            List of chunked documents with preserved metadata
        """
        chunked_documents = []

        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})

            if not content:
                continue

            chunks = self.chunk_text(content)

            for i, chunk in enumerate(chunks):
                chunked_doc = {
                    "content": chunk,
                    "metadata": {
                        **metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                }
                chunked_documents.append(chunked_doc)

        logger.info(f"Created {len(chunked_documents)} chunks from {len(documents)} documents")
        return chunked_documents
