#!/usr/bin/env python3
"""
Test script to verify RAG system is working correctly
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
    RAG_CHUNK_OVERLAP,
    RAG_TOP_K
)

def main():
    print("=" * 80)
    print("RAG System Test")
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

    # Get status
    print("Getting RAG system status...")
    status = retriever.get_status()
    print(f"✓ RAG Enabled: {status['enabled']}")
    print(f"✓ Documents in knowledge base: {status['documents_in_knowledge_base']}")
    print(f"✓ Chunks in vector store: {status['chunks_in_vector_store']}")
    print(f"✓ Persist directory: {status['persist_directory']}")
    print()

    # Test query
    test_query = "What are the key considerations for agent quality and evaluation?"
    print(f"Test Query: '{test_query}'")
    print()

    print("Retrieving relevant documents...")
    documents = retriever.retrieve(test_query, top_k=RAG_TOP_K)
    print(f"✓ Retrieved {len(documents)} documents")
    print()

    # Format with citations
    print("Formatting context with citations...")
    context, citations = retriever.format_context_with_citations(documents)
    print(f"✓ Generated context with {len(citations)} citations")
    print()

    # Display results
    print("=" * 80)
    print("Retrieved Context:")
    print("=" * 80)
    print(context)
    print()

    print("=" * 80)
    print("Citations:")
    print("=" * 80)
    for citation in citations:
        print(f"[{citation['id']}] {citation['document']}")
        print(f"    Section: {citation['section']}")
        print(f"    Page: {citation['page']}")
        print(f"    Relevance Score: {citation['relevance_score']}")
        print()

    print("=" * 80)
    print("✓ RAG System Test Complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
