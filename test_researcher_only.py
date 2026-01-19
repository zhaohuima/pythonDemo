#!/usr/bin/env python3
"""
Simple test script to test ProductResearcher agent only (no RAG, no full workflow)
"""

import os
import sys
import json

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import ProductResearcher, init_llm

def main():
    print("=" * 80)
    print("Product Researcher Agent Test (No RAG)")
    print("=" * 80)
    print()

    # Test product idea
    product_idea = """
    I'm building an AI customer support agent for e-commerce companies.
    What are the key user pain points I should solve, and who are my main competitors?
    """

    print("Product Idea:")
    print(product_idea)
    print()
    print("=" * 80)
    print()

    # Initialize LLM
    print("Initializing LLM...")
    llm = init_llm()
    print("✓ LLM initialized")
    print()

    # Initialize ProductResearcher
    print("Initializing ProductResearcher...")
    researcher = ProductResearcher(llm)
    print("✓ ProductResearcher initialized")
    print()

    # Run research
    print("=" * 80)
    print("Running Product Research...")
    print("=" * 80)
    print()

    try:
        result = researcher.research(product_idea)

        print()
        print("=" * 80)
        print("Research Complete!")
        print("=" * 80)
        print()

        # Display results
        if "research_result" in result:
            research_result = result["research_result"]

            print("📊 PRODUCT RESEARCH RESULTS:")
            print("-" * 80)
            print()

            if "core_requirements" in research_result:
                print("1. CORE REQUIREMENTS:")
                print(research_result["core_requirements"])
                print()

            if "target_users" in research_result:
                print("2. TARGET USERS:")
                print(research_result["target_users"])
                print()

            if "market_analysis" in research_result:
                print("3. MARKET ANALYSIS:")
                print(research_result["market_analysis"])
                print()

            if "market_insights" in research_result:
                print("4. MARKET INSIGHTS:")
                print(research_result["market_insights"])
                print()

        print("=" * 80)
        print("✓ Test Complete!")
        print("=" * 80)
        print()

        # Print agent info
        print(f"Agent Type: {result.get('agent_type', 'unknown')}")
        print(f"Status: {result.get('status', 'unknown')}")

    except Exception as e:
        print(f"❌ Error during research: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
