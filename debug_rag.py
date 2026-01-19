#!/usr/bin/env python3
"""
RAG Debug Script - Step by Step Verification
逐步调试RAG系统的每一个环节
"""

import logging
import sys

# 设置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_separator(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def step1_check_documents():
    """Step 1: 检查文档加载"""
    print_separator("Step 1: Document Loading")

    from rag.document_loader import PDFLoader
    from config import RAG_DOCUMENTS_DIR

    loader = PDFLoader(RAG_DOCUMENTS_DIR)

    # 检查文档目录
    doc_list = loader.get_document_list()
    print(f"Found {len(doc_list)} PDF files in {RAG_DOCUMENTS_DIR}:")
    for doc in doc_list:
        print(f"  - {doc['filename']} ({doc['size_mb']} MB)")

    if not doc_list:
        print("ERROR: No PDF documents found!")
        return None

    # 加载所有文档
    print("\nLoading all documents...")
    documents = loader.load_all_documents()
    print(f"Loaded {len(documents)} pages from all documents")

    if documents:
        print("\nSample document (first page):")
        print(f"  Source: {documents[0]['metadata']['source']}")
        print(f"  Page: {documents[0]['metadata']['page']}")
        print(f"  Section: {documents[0]['metadata']['section']}")
        print(f"  Content preview: {documents[0]['content'][:200]}...")

    return documents

def step2_check_chunking(documents):
    """Step 2: 检查文档分块"""
    print_separator("Step 2: Text Chunking")

    if not documents:
        print("ERROR: No documents to chunk!")
        return None

    from rag.text_chunker import TextChunker
    from config import RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP

    chunker = TextChunker(RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP)

    print(f"Chunk size: {RAG_CHUNK_SIZE}, Overlap: {RAG_CHUNK_OVERLAP}")
    print(f"Input: {len(documents)} pages")

    chunked_docs = chunker.chunk_documents(documents)
    print(f"Output: {len(chunked_docs)} chunks")

    if chunked_docs:
        print("\nSample chunks:")
        for i, chunk in enumerate(chunked_docs[:3]):
            print(f"\n  Chunk {i+1}:")
            print(f"    Source: {chunk['metadata']['source']}")
            print(f"    Page: {chunk['metadata']['page']}")
            print(f"    Chunk index: {chunk['metadata']['chunk_index']}/{chunk['metadata']['total_chunks']}")
            print(f"    Content length: {len(chunk['content'])} chars")
            print(f"    Content preview: {chunk['content'][:100]}...")

    return chunked_docs

def step3_check_embeddings(chunked_docs):
    """Step 3: 检查Embedding生成"""
    print_separator("Step 3: Embedding Generation")

    if not chunked_docs:
        print("ERROR: No chunks to embed!")
        return None

    from rag.embeddings import EmbeddingModel
    from config import RAG_EMBEDDING_MODEL

    print(f"Embedding model: {RAG_EMBEDDING_MODEL}")

    embeddings_model = EmbeddingModel(RAG_EMBEDDING_MODEL)

    # 只测试前3个chunk
    test_texts = [doc['content'] for doc in chunked_docs[:3]]
    print(f"Testing embedding generation for {len(test_texts)} chunks...")

    embeddings = embeddings_model.embed_texts(test_texts)

    print(f"Generated {len(embeddings)} embeddings")
    if embeddings:
        print(f"Embedding dimension: {len(embeddings[0])}")
        print(f"Sample embedding (first 10 values): {embeddings[0][:10]}")

    return embeddings_model

def step4_check_vector_store():
    """Step 4: 检查ChromaDB存储"""
    print_separator("Step 4: ChromaDB Vector Store")

    from rag.vector_store import VectorStore
    from config import RAG_VECTOR_DB_DIR, RAG_COLLECTION_NAME

    print(f"Vector DB directory: {RAG_VECTOR_DB_DIR}")
    print(f"Collection name: {RAG_COLLECTION_NAME}")

    vector_store = VectorStore(RAG_VECTOR_DB_DIR, RAG_COLLECTION_NAME)

    stats = vector_store.get_stats()
    print(f"\nVector store stats:")
    print(f"  Collection: {stats['collection_name']}")
    print(f"  Document count: {stats['document_count']}")
    print(f"  Persist directory: {stats['persist_directory']}")

    if stats['document_count'] == 0:
        print("\nWARNING: Vector store is EMPTY! Documents need to be indexed.")
        return None

    return vector_store

def step5_check_retrieval(vector_store, embeddings_model):
    """Step 5: 检查检索功能"""
    print_separator("Step 5: Document Retrieval")

    if not vector_store or not embeddings_model:
        print("ERROR: Vector store or embeddings model not available!")
        return None

    from config import RAG_TOP_K

    # 测试查询
    test_query = "What is an AI agent and how does it work?"
    print(f"Test query: '{test_query}'")
    print(f"Top K: {RAG_TOP_K}")

    # 生成查询embedding
    query_embedding = embeddings_model.embed_query(test_query)
    print(f"Query embedding dimension: {len(query_embedding)}")

    # 检索
    results = vector_store.query(query_embedding, top_k=RAG_TOP_K)

    print(f"\nRetrieved {len(results)} documents:")
    for i, doc in enumerate(results):
        print(f"\n  Result {i+1}:")
        print(f"    ID: {doc['id']}")
        print(f"    Score: {doc['score']:.4f}")
        print(f"    Source: {doc['metadata'].get('source', 'N/A')}")
        print(f"    Page: {doc['metadata'].get('page', 'N/A')}")
        print(f"    Content preview: {doc['content'][:150]}...")

    return results

def step6_check_rag_retriever():
    """Step 6: 检查完整的RAG Retriever"""
    print_separator("Step 6: Full RAG Retriever")

    from rag import RAGRetriever
    from config import (RAG_DOCUMENTS_DIR, RAG_VECTOR_DB_DIR, RAG_COLLECTION_NAME,
                       RAG_EMBEDDING_MODEL, RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP, RAG_TOP_K)

    retriever = RAGRetriever(
        documents_dir=RAG_DOCUMENTS_DIR,
        persist_directory=RAG_VECTOR_DB_DIR,
        collection_name=RAG_COLLECTION_NAME,
        embedding_model=RAG_EMBEDDING_MODEL,
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP
    )

    # 获取状态
    status = retriever.get_status()
    print("RAG Retriever Status:")
    print(f"  Enabled: {status['enabled']}")
    print(f"  Documents in knowledge base: {status['documents_in_knowledge_base']}")
    print(f"  Chunks in vector store: {status['chunks_in_vector_store']}")

    if status['chunks_in_vector_store'] == 0:
        print("\nVector store is empty. Running document ingestion...")
        result = retriever.ingest_documents(clear_existing=True)
        print(f"Ingestion result: {result}")

        # 重新获取状态
        status = retriever.get_status()
        print(f"\nAfter ingestion - Chunks in vector store: {status['chunks_in_vector_store']}")

    # 测试检索
    test_query = "What is an AI agent and how does it work?"
    print(f"\nTest retrieval with query: '{test_query}'")

    results = retriever.retrieve(test_query, top_k=RAG_TOP_K)
    print(f"Retrieved {len(results)} documents")

    if results:
        context, citations = retriever.format_context_with_citations(results)
        print(f"\nFormatted context length: {len(context)} chars")
        print(f"Number of citations: {len(citations)}")
        print("\nCitations:")
        for cite in citations:
            print(f"  [{cite['id']}] {cite['document']}, {cite['section']} (Page {cite['page']}) - Score: {cite['relevance_score']}")

        print("\nContext preview:")
        print(context[:500] + "...")

    return retriever

def step7_check_agent_integration():
    """Step 7: 检查Agent集成"""
    print_separator("Step 7: Agent Integration (FeasibilityEvaluator)")

    from agents import FeasibilityEvaluator, init_llm
    from rag import RAGRetriever
    from config import (RAG_DOCUMENTS_DIR, RAG_VECTOR_DB_DIR, RAG_COLLECTION_NAME,
                       RAG_EMBEDDING_MODEL, RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP)

    # 初始化RAG
    rag_retriever = RAGRetriever(
        documents_dir=RAG_DOCUMENTS_DIR,
        persist_directory=RAG_VECTOR_DB_DIR,
        collection_name=RAG_COLLECTION_NAME,
        embedding_model=RAG_EMBEDDING_MODEL,
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP
    )

    # 检查vector store状态
    status = rag_retriever.get_status()
    print(f"RAG Status - Chunks in vector store: {status['chunks_in_vector_store']}")

    if status['chunks_in_vector_store'] == 0:
        print("ERROR: Vector store is empty! Please run step 6 first to ingest documents.")
        return

    # 初始化LLM和Agent
    print("\nInitializing LLM and FeasibilityEvaluator...")
    llm = init_llm()
    evaluator = FeasibilityEvaluator(llm, rag_retriever)

    print(f"RAG enabled in evaluator: {evaluator.rag_retriever is not None}")

    # 测试评估（简化版，不实际调用LLM）
    test_input = "Build an AI-powered customer service chatbot"
    test_research = {
        "core_requirements": "AI chatbot for customer service",
        "market_analysis": "Growing market for AI chatbots",
        "target_users": "Enterprise customers",
        "market_insights": "High demand for automation"
    }

    print(f"\nTest input: '{test_input}'")
    print("Note: Full evaluation would call LLM. Here we just verify RAG retrieval works.")

    # 手动测试RAG检索部分
    query = f"{test_input} technical feasibility cost architecture risk compliance"
    print(f"\nRAG query: '{query[:80]}...'")

    from config import RAG_TOP_K
    retrieved_docs = rag_retriever.retrieve(query, top_k=RAG_TOP_K)

    if retrieved_docs:
        rag_context, citations = rag_retriever.format_context_with_citations(retrieved_docs)
        print(f"\nRAG retrieval successful!")
        print(f"  Retrieved {len(retrieved_docs)} documents")
        print(f"  Context length: {len(rag_context)} chars")
        print(f"  Citations: {len(citations)}")

        print("\nThis context would be injected into the FeasibilityEvaluator prompt.")
    else:
        print("\nWARNING: RAG retrieval returned no documents!")

def main():
    print("\n" + "#"*80)
    print("#" + " "*30 + "RAG DEBUG SCRIPT" + " "*32 + "#")
    print("#"*80)

    try:
        # Step 1: 文档加载
        documents = step1_check_documents()
        if not documents:
            print("\nSTOPPED: No documents loaded. Please add PDF files to knowledge_base/documents/")
            return

        # Step 2: 文档分块
        chunked_docs = step2_check_chunking(documents)
        if not chunked_docs:
            print("\nSTOPPED: Chunking failed.")
            return

        # Step 3: Embedding生成
        embeddings_model = step3_check_embeddings(chunked_docs)
        if not embeddings_model:
            print("\nSTOPPED: Embedding generation failed.")
            return

        # Step 4: Vector Store检查
        vector_store = step4_check_vector_store()

        # Step 5: 检索测试（如果vector store有数据）
        if vector_store:
            step5_check_retrieval(vector_store, embeddings_model)

        # Step 6: 完整RAG Retriever测试
        retriever = step6_check_rag_retriever()

        # Step 7: Agent集成测试
        if retriever:
            step7_check_agent_integration()

        print_separator("DEBUG COMPLETE")
        print("If all steps passed, RAG should be working correctly.")
        print("If vector store was empty, documents have been indexed.")
        print("\nNext steps:")
        print("1. Restart web_app.py")
        print("2. Test again at http://localhost:5000")

    except Exception as e:
        logger.exception(f"Debug failed with error: {e}")
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
