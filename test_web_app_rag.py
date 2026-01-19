#!/usr/bin/env python3
"""
Test RAG integration in web_app context
测试web_app中的RAG集成
"""

import logging
import sys

# 设置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_web_app_rag():
    """模拟web_app中的RAG初始化和使用"""

    print("\n" + "="*80)
    print("Testing RAG Integration in web_app context")
    print("="*80 + "\n")

    # Step 1: 模拟web_app中的RAG初始化
    print("Step 1: Simulating web_app RAG initialization...")

    from config import (RAG_ENABLED, RAG_DOCUMENTS_DIR, RAG_VECTOR_DB_DIR,
                       RAG_COLLECTION_NAME, RAG_EMBEDDING_MODEL,
                       RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP)

    print(f"  RAG_ENABLED: {RAG_ENABLED}")
    print(f"  RAG_DOCUMENTS_DIR: {RAG_DOCUMENTS_DIR}")
    print(f"  RAG_VECTOR_DB_DIR: {RAG_VECTOR_DB_DIR}")

    rag_retriever = None
    if RAG_ENABLED:
        try:
            from rag import RAGRetriever
            rag_retriever = RAGRetriever(
                documents_dir=RAG_DOCUMENTS_DIR,
                persist_directory=RAG_VECTOR_DB_DIR,
                collection_name=RAG_COLLECTION_NAME,
                embedding_model=RAG_EMBEDDING_MODEL,
                chunk_size=RAG_CHUNK_SIZE,
                chunk_overlap=RAG_CHUNK_OVERLAP
            )
            print("  ✓ RAG Retriever initialized successfully")

            # 检查状态
            status = rag_retriever.get_status()
            print(f"  Chunks in vector store: {status['chunks_in_vector_store']}")

        except Exception as e:
            print(f"  ✗ Failed to initialize RAG Retriever: {e}")
            import traceback
            traceback.print_exc()
            return
    else:
        print("  RAG is disabled in config")
        return

    # Step 2: 模拟StreamingOrchestrator中的Agent初始化
    print("\nStep 2: Simulating StreamingOrchestrator Agent initialization...")

    from agents import ProductResearcher, DocAssistant, FeasibilityEvaluator, init_llm

    llm = init_llm()
    print("  ✓ LLM initialized")

    researcher = ProductResearcher(llm)
    print("  ✓ ProductResearcher initialized")

    doc_assistant = DocAssistant(llm)
    print("  ✓ DocAssistant initialized")

    # 关键：传递rag_retriever给FeasibilityEvaluator
    evaluator = FeasibilityEvaluator(llm, rag_retriever)
    print(f"  ✓ FeasibilityEvaluator initialized")
    print(f"    - rag_retriever is not None: {evaluator.rag_retriever is not None}")

    # Step 3: 测试FeasibilityEvaluator的RAG检索
    print("\nStep 3: Testing FeasibilityEvaluator RAG retrieval...")

    test_input = "Build an AI-powered customer service chatbot"
    test_research = {
        "core_requirements": "AI chatbot for customer service",
        "market_analysis": "Growing market for AI chatbots",
        "target_users": "Enterprise customers",
        "market_insights": "High demand for automation"
    }

    print(f"  Test input: '{test_input}'")

    # 手动测试RAG检索部分（不调用LLM）
    if evaluator.rag_retriever:
        from config import RAG_TOP_K

        query = f"{test_input} technical feasibility cost architecture risk compliance"
        print(f"  RAG query: '{query[:60]}...'")

        retrieved_docs = evaluator.rag_retriever.retrieve(query, top_k=RAG_TOP_K)

        if retrieved_docs:
            rag_context, citations = evaluator.rag_retriever.format_context_with_citations(retrieved_docs)
            print(f"\n  ✓ RAG retrieval successful!")
            print(f"    - Retrieved {len(retrieved_docs)} documents")
            print(f"    - Context length: {len(rag_context)} chars")
            print(f"    - Citations: {len(citations)}")

            print("\n  Citations:")
            for cite in citations:
                print(f"    [{cite['id']}] {cite['document']}, Page {cite['page']} - Score: {cite['relevance_score']:.3f}")

            print("\n  Context preview (first 500 chars):")
            print("  " + "-"*60)
            print("  " + rag_context[:500].replace('\n', '\n  '))
            print("  " + "-"*60)
        else:
            print("\n  ✗ RAG retrieval returned no documents!")
    else:
        print("\n  ✗ RAG retriever is None in FeasibilityEvaluator!")

    # Step 4: 完整测试（调用LLM）
    print("\nStep 4: Full evaluation test (calls LLM)...")
    print("  This will take some time as it calls the LLM API...")

    try:
        result = evaluator.evaluate(test_input, test_research)

        print(f"\n  ✓ Evaluation completed!")
        print(f"    - RAG enabled: {result.get('rag_enabled', False)}")
        print(f"    - Citations count: {result.get('citations_count', 0)}")

        eval_result = result.get('evaluation_result', {})
        if 'citations' in eval_result:
            print(f"    - Citations in result: {len(eval_result['citations'])}")

        # 检查评估结果中是否有引用标记
        for key, value in eval_result.items():
            if key != 'citations' and isinstance(value, str):
                if '[1]' in value or '[2]' in value:
                    print(f"    - Found citation markers in '{key}'")

    except Exception as e:
        print(f"\n  ✗ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)
    print("Test completed!")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_web_app_rag()
