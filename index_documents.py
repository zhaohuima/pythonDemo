#!/usr/bin/env python3
"""
Script to index PDF documents into the vector database
"""

import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag import RAGRetriever
from config import (
    RAG_DOCUMENTS_DIR,
    RAG_VECTOR_DB_DIR,
    RAG_COLLECTION_NAME,
    RAG_EMBEDDING_MODEL,
    RAG_CHUNK_SIZE,
    RAG_CHUNK_OVERLAP
)

def main():
    print("=" * 80)
    print("Document Indexing Script")
    print("=" * 80)
    print()

    # Initialize RAG retriever
    print("Initializing RAG Retriever...")
    retriever = RAGRetriever(
        documents_dir=RAG_DOCUMENTS_DIR,
        persist_directory=RAG_VECTOR_DB_DIR,
        collection_name=RAG_COLLECTION_NAME,
        embedding_model=RAG_EMBEDDING_MODEL,
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP
    )
    print("✓ RAG Retriever initialized")
    print()

    # Index documents
    print("Starting document indexing...")
    print(f"Documents directory: {RAG_DOCUMENTS_DIR}")
    print(f"Vector DB directory: {RAG_VECTOR_DB_DIR}")
    print()

    result = retriever.ingest_documents(clear_existing=True)

    print()
    print("=" * 80)
    print("Indexing Results:")
    print("=" * 80)
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Documents processed: {result.get('documents_processed', 0)}")
    print(f"Pages processed: {result.get('pages_processed', 0)}")
    print(f"Chunks created: {result.get('chunks_created', 0)}")

    if 'document_names' in result:
        print()
        print("Documents indexed:")
        for doc_name in result['document_names']:
            print(f"  - {doc_name}")

    print()
    print("=" * 80)
    print("✓ Indexing complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
