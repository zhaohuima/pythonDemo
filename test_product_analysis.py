#!/usr/bin/env python3
"""
Test script to run a complete product analysis with RAG
"""

import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langgraph_orchestrator import LangGraphOrchestrator
from agents import ProductResearcher, DocAssistant, FeasibilityEvaluator, init_llm
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
    print("Product Analysis Test with RAG")
    print("=" * 80)
    print()

    # Test product idea
    product_idea = """
    An AI-powered customer service agent that can handle complex multi-turn
    conversations, integrate with existing CRM systems, and provide personalized
    responses based on customer history. The agent should be able to escalate
    to human agents when needed and maintain context across multiple sessions.
    """

    print("Product Idea:")
    print(product_idea)
    print()
    print("=" * 80)
    print()

    # Initialize RAG retriever
    print("Initializing RAG Retriever...")
    rag_retriever = RAGRetriever(
        documents_dir=RAG_DOCUMENTS_DIR,
        persist_directory=RAG_VECTOR_DB_DIR,
        collection_name=RAG_COLLECTION_NAME,
        embedding_model=RAG_EMBEDDING_MODEL,
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP
    )
    print("✓ RAG Retriever initialized")
    print()

    # Initialize LLM
    print("Initializing LLM...")
    llm = init_llm()
    print("✓ LLM initialized")
    print()

    # Initialize agents
    print("Initializing agents...")
    researcher = ProductResearcher(llm)
    doc_assistant = DocAssistant(llm)
    evaluator = FeasibilityEvaluator(llm, rag_retriever=rag_retriever)
    print("✓ Agents initialized")
    print()

    # Initialize orchestrator
    print("Initializing orchestrator...")
    orchestrator = LangGraphOrchestrator(researcher, doc_assistant, evaluator)
    print("✓ Orchestrator initialized")
    print()

    # Run analysis
    print("=" * 80)
    print("Running Product Analysis...")
    print("=" * 80)
    print()

    try:
        result = orchestrator.execute_workflow(product_idea)

        print()
        print("=" * 80)
        print("Analysis Complete!")
        print("=" * 80)
        print()

        # Display results
        if "research_output" in result:
            print("📊 PRODUCT RESEARCH:")
            print("-" * 80)
            print(result["research_output"])
            print()

        if "evaluation_output" in result:
            print("🔍 FEASIBILITY EVALUATION:")
            print("-" * 80)
            print(result["evaluation_output"])
            print()

        if "evaluation_citations" in result:
            print("📚 CITATIONS:")
            print("-" * 80)
            for citation in result["evaluation_citations"]:
                print(f"[{citation['id']}] {citation['document']}")
                print(f"    Section: {citation['section']}")
                print(f"    Page: {citation['page']}")
                print(f"    Relevance Score: {citation.get('relevance_score', 'N/A')}")
                print()

        if "documentation_output" in result:
            print("📝 DOCUMENTATION:")
            print("-" * 80)
            print(result["documentation_output"])
            print()

        print("=" * 80)
        print("✓ Test Complete!")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
