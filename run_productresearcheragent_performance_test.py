#!/usr/bin/env python3
"""
Performance Test Runner
Main script to orchestrate the entire testing workflow
"""

import argparse
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_case_loader import load_test_cases_from_pdf
from agent_executor import AgentExecutor
from llm_scorer import LLMScorer
from report_generator import ReportGenerator


def main():
    """Main test runner"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run Product Researcher Agent Performance Tests")
    parser.add_argument(
        "--pdf-path",
        default="Product Master Test Case-User and market Research.pdf",
        help="Path to PDF with test cases"
    )
    parser.add_argument(
        "--output-dir",
        default="test_results",
        help="Output directory for reports"
    )
    parser.add_argument(
        "--test-ids",
        help="Run specific test IDs only (comma-separated, e.g., '1.1,1.2,2.3')"
    )
    parser.add_argument(
        "--category",
        help="Run tests for specific category only"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output during execution"
    )

    args = parser.parse_args()

    # Print header
    print("=" * 80)
    print("Product Researcher Agent Performance Test")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Step 1: Load test cases from PDF
    print("[1/4] Loading test cases from PDF...")
    try:
        all_test_cases = load_test_cases_from_pdf(args.pdf_path)
        print(f"  ✓ Loaded {len(all_test_cases)} test cases")
    except Exception as e:
        print(f"  ✗ Error loading test cases: {e}")
        return 1

    # Filter test cases if needed
    test_cases = all_test_cases
    if args.test_ids:
        test_ids = [tid.strip() for tid in args.test_ids.split(',')]
        test_cases = [tc for tc in all_test_cases if tc.id in test_ids]
        print(f"  ✓ Filtered to {len(test_cases)} test cases: {', '.join(test_ids)}")

    if args.category:
        test_cases = [tc for tc in test_cases if tc.category == args.category]
        print(f"  ✓ Filtered to {len(test_cases)} test cases in category: {args.category}")

    if not test_cases:
        print("  ✗ No test cases to run!")
        return 1

    print()

    # Step 2: Initialize components
    print("[2/4] Initializing components...")
    try:
        executor = AgentExecutor()
        scorer = LLMScorer()
        print("  ✓ Agent executor initialized")
        print("  ✓ LLM scorer initialized")
    except Exception as e:
        print(f"  ✗ Error initializing components: {e}")
        return 1

    print()

    # Step 3: Execute tests sequentially
    print(f"[3/4] Running {len(test_cases)} test cases...")
    print()

    results = []
    failed_tests = []

    for i, test_case in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] Test {test_case.id}: {test_case.name}")
        print(f"  Category: {test_case.category}")

        if args.verbose:
            print(f"  Question: {test_case.user_question[:100]}...")

        try:
            # Execute agent
            agent_output = executor.execute_agent(test_case)

            if agent_output.status == "success":
                print(f"  ✓ Agent execution completed ({agent_output.execution_time:.1f}s)")

                # Score output
                test_score = scorer.score_output(agent_output, test_case)
                results.append(test_score)

                print(f"  ✓ Scoring completed ({test_score.execution_time:.1f}s)")
                print(f"  Score: {test_score.total_score}/40 ({test_score.total_score/40*100:.1f}%)")
                print(f"    - User Requirements: {test_score.dimension_a_score}/10")
                print(f"    - Target Users: {test_score.dimension_b_score}/10")
                print(f"    - Market Analysis: {test_score.dimension_c_score}/10")
                print(f"    - Market Insights: {test_score.dimension_d_score}/10")

            else:
                print(f"  ✗ Agent execution failed: {agent_output.error_message}")
                failed_tests.append({
                    'id': test_case.id,
                    'name': test_case.name,
                    'error': agent_output.error_message
                })

        except Exception as e:
            print(f"  ✗ Error during test: {e}")
            failed_tests.append({
                'id': test_case.id,
                'name': test_case.name,
                'error': str(e)
            })

        print()

    # Step 4: Generate reports
    print("[4/4] Generating reports...")

    if results:
        try:
            generator = ReportGenerator(output_dir=args.output_dir)
            report_path, csv_path, excel_path = generator.generate_all_reports(results, test_cases)

            print()
            print("=" * 80)
            print("Test Results Summary")
            print("=" * 80)
            print(f"Total tests run: {len(test_cases)}")
            print(f"Successful: {len(results)}")
            print(f"Failed: {len(failed_tests)}")

            if results:
                avg_score = sum(r.total_score for r in results) / len(results)
                print(f"Average score: {avg_score:.1f}/40 ({avg_score/40*100:.1f}%)")

                passed = sum(1 for r in results if r.total_score >= 28)
                pass_rate = (passed / len(results)) * 100
                print(f"Pass rate (≥28/40): {pass_rate:.1f}%")

            print()
            print("Reports generated:")
            print(f"  - Detailed report: {report_path}")
            print(f"  - CSV export: {csv_path}")
            print(f"  - Excel export: {excel_path}")

            if failed_tests:
                print()
                print("Failed tests:")
                for failed in failed_tests:
                    print(f"  - {failed['id']}: {failed['name']}")
                    print(f"    Error: {failed['error']}")

            print()
            print("=" * 80)
            print("✓ Testing complete!")
            print("=" * 80)

            return 0

        except Exception as e:
            print(f"  ✗ Error generating reports: {e}")
            import traceback
            traceback.print_exc()
            return 1

    else:
        print("  ✗ No successful test results to report")
        return 1


if __name__ == "__main__":
    sys.exit(main())
