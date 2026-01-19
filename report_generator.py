#!/usr/bin/env python3
"""
Report Generator
Generates detailed reports and exports (CSV, Excel)
"""

import os
from datetime import datetime
from typing import List
import pandas as pd


class ReportGenerator:
    """Generates test reports and exports"""

    def __init__(self, output_dir: str = "test_results"):
        """
        Initialize report generator

        Args:
            output_dir: Directory to save reports (default: test_results)
        """
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

    def generate_all_reports(self, results: List, test_cases: List = None):
        """
        Generate all reports and exports

        Args:
            results: List of TestScore objects
            test_cases: Optional list of TestCase objects for additional context
        """
        print("\nGenerating reports...")

        # Store test_cases for use in report generation
        self.test_cases_dict = {}
        if test_cases:
            for tc in test_cases:
                self.test_cases_dict[tc.id] = tc

        # Generate detailed markdown report
        report_path = self.generate_detailed_report(results)
        print(f"  ✓ Detailed report: {report_path}")

        # Export to CSV
        csv_path = self.export_to_csv(results)
        print(f"  ✓ CSV export: {csv_path}")

        # Export to Excel
        excel_path = self.export_to_excel(results)
        print(f"  ✓ Excel export: {excel_path}")

        return report_path, csv_path, excel_path

    def generate_detailed_report(self, results: List) -> str:
        """
        Generate detailed markdown report

        Args:
            results: List of TestScore objects

        Returns:
            Path to generated report
        """
        # Calculate statistics
        stats = self._calculate_statistics(results)

        # Build report content
        report_lines = []
        report_lines.append("# Product Researcher Agent Performance Test Report")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # Executive Summary
        report_lines.append("## Executive Summary")
        report_lines.append(f"- **Total Test Cases**: {stats['total_tests']}")
        report_lines.append(f"- **Average Score**: {stats['avg_score']:.1f}/40 ({stats['avg_percentage']:.1f}%)")
        report_lines.append(f"- **Pass Rate (≥28/40)**: {stats['pass_rate']:.1f}%")

        # Add scorer model information
        if results and results[0].scorer_model:
            report_lines.append(f"- **Scoring Model**: {results[0].scorer_model}")

        report_lines.append(f"- **Dimension Averages**:")
        report_lines.append(f"  - User Requirements: {stats['avg_dim_a']:.1f}/10")
        report_lines.append(f"  - Target Users: {stats['avg_dim_b']:.1f}/10")
        report_lines.append(f"  - Market Analysis: {stats['avg_dim_c']:.1f}/10")
        report_lines.append(f"  - Market Insights: {stats['avg_dim_d']:.1f}/10")
        report_lines.append("")

        # Category Breakdown
        report_lines.append("## Category Breakdown")
        for category, cat_stats in stats['by_category'].items():
            report_lines.append(f"### {category}")
            report_lines.append(f"- **Tests**: {cat_stats['count']}")
            report_lines.append(f"- **Average Score**: {cat_stats['avg_score']:.1f}/40 ({cat_stats['avg_percentage']:.1f}%)")
            if cat_stats['best']:
                report_lines.append(f"- **Best**: Test {cat_stats['best']['id']} ({cat_stats['best']['score']}/40)")
            if cat_stats['worst']:
                report_lines.append(f"- **Worst**: Test {cat_stats['worst']['id']} ({cat_stats['worst']['score']}/40)")
            report_lines.append("")

        # Individual Test Results
        report_lines.append("## Individual Test Results")
        for result in sorted(results, key=lambda x: x.test_case_id):
            report_lines.append(f"### Test {result.test_case_id}: {result.test_name}")
            report_lines.append(f"- **Category**: {result.category}")
            report_lines.append(f"- **Total Score**: {result.total_score}/40 ({result.total_score/40*100:.1f}%)")
            report_lines.append("")

            # Add User Query
            if result.user_question:
                report_lines.append("#### User Query")
                report_lines.append("```")
                report_lines.append(str(result.user_question))
                report_lines.append("```")
                report_lines.append("")

            # Get test case for standard answers
            test_case = self.test_cases_dict.get(result.test_case_id)

            # Dimension A: User Requirements
            report_lines.append(f"#### Dimension A: User Requirements - {result.dimension_a_score}/10")
            report_lines.append("")
            if result.agent_user_requirements:
                report_lines.append("**Agent Response:**")
                report_lines.append("```")
                report_lines.append(str(result.agent_user_requirements))
                report_lines.append("```")
                report_lines.append("")
            if test_case and test_case.standard_answer.user_requirements:
                report_lines.append("**Standard Answer:**")
                report_lines.append("```")
                report_lines.append(str(test_case.standard_answer.user_requirements))
                report_lines.append("```")
                report_lines.append("")
            report_lines.append(f"**Scoring Reasoning:** {result.dimension_a_reasoning}")
            report_lines.append("")

            # Dimension B: Target Users
            report_lines.append(f"#### Dimension B: Target Users - {result.dimension_b_score}/10")
            report_lines.append("")
            if result.agent_target_users:
                report_lines.append("**Agent Response:**")
                report_lines.append("```")
                report_lines.append(str(result.agent_target_users))
                report_lines.append("```")
                report_lines.append("")
            if test_case and test_case.standard_answer.target_users:
                report_lines.append("**Standard Answer:**")
                report_lines.append("```")
                report_lines.append(str(test_case.standard_answer.target_users))
                report_lines.append("```")
                report_lines.append("")
            report_lines.append(f"**Scoring Reasoning:** {result.dimension_b_reasoning}")
            report_lines.append("")

            # Dimension C: Market Analysis
            report_lines.append(f"#### Dimension C: Market Analysis - {result.dimension_c_score}/10")
            report_lines.append("")
            if result.agent_market_competitors:
                report_lines.append("**Agent Response:**")
                report_lines.append("```")
                report_lines.append(str(result.agent_market_competitors))
                report_lines.append("```")
                report_lines.append("")
            if test_case and test_case.standard_answer.market_competitors:
                report_lines.append("**Standard Answer:**")
                report_lines.append("```")
                report_lines.append(str(test_case.standard_answer.market_competitors))
                report_lines.append("```")
                report_lines.append("")
            report_lines.append(f"**Scoring Reasoning:** {result.dimension_c_reasoning}")
            report_lines.append("")

            # Dimension D: Market Insights
            report_lines.append(f"#### Dimension D: Market Insights - {result.dimension_d_score}/10")
            report_lines.append("")
            if result.agent_market_insights:
                report_lines.append("**Agent Response:**")
                report_lines.append("```")
                report_lines.append(str(result.agent_market_insights))
                report_lines.append("```")
                report_lines.append("")
            if test_case and test_case.standard_answer.market_insights:
                report_lines.append("**Standard Answer:**")
                report_lines.append("```")
                report_lines.append(str(test_case.standard_answer.market_insights))
                report_lines.append("```")
                report_lines.append("")
            report_lines.append(f"**Scoring Reasoning:** {result.dimension_d_reasoning}")
            report_lines.append("")

            report_lines.append("---")
            report_lines.append("")

        # Low-Scoring Tests
        low_scoring = [r for r in results if r.total_score < 28]
        if low_scoring:
            report_lines.append("## Low-Scoring Tests (Score < 28/40)")
            report_lines.append(f"Found {len(low_scoring)} test(s) that need improvement:")
            for result in sorted(low_scoring, key=lambda x: x.total_score):
                report_lines.append(f"- **Test {result.test_case_id}**: {result.test_name} - {result.total_score}/40")
                report_lines.append(f"  - Weakest dimension: {self._find_weakest_dimension(result)}")
            report_lines.append("")

        # Save report
        report_path = os.path.join(self.output_dir, f"detailed_report_{self.timestamp}.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        return report_path

    def export_to_csv(self, results: List) -> str:
        """
        Export results to CSV

        Args:
            results: List of TestScore objects

        Returns:
            Path to CSV file
        """
        # Prepare data
        data = []
        for result in results:
            data.append({
                'Test ID': result.test_case_id,
                'Test Name': result.test_name,
                'Category': result.category,
                'Dim A (User Req)': result.dimension_a_score,
                'Dim B (Target Users)': result.dimension_b_score,
                'Dim C (Market Analysis)': result.dimension_c_score,
                'Dim D (Market Insights)': result.dimension_d_score,
                'Total Score': result.total_score,
                'Percentage': f"{result.total_score/40*100:.1f}%",
                'Status': 'Pass' if result.total_score >= 28 else 'Fail'
            })

        # Create DataFrame and save
        df = pd.DataFrame(data)
        csv_path = os.path.join(self.output_dir, f"test_scores_{self.timestamp}.csv")
        df.to_csv(csv_path, index=False)

        return csv_path

    def export_to_excel(self, results: List) -> str:
        """
        Export results to Excel with multiple sheets

        Args:
            results: List of TestScore objects

        Returns:
            Path to Excel file
        """
        excel_path = os.path.join(self.output_dir, f"test_results_{self.timestamp}.xlsx")

        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Summary sheet
            stats = self._calculate_statistics(results)
            summary_data = {
                'Metric': [
                    'Total Test Cases',
                    'Average Score',
                    'Pass Rate (≥28/40)',
                    'Avg User Requirements',
                    'Avg Target Users',
                    'Avg Market Analysis',
                    'Avg Market Insights'
                ],
                'Value': [
                    stats['total_tests'],
                    f"{stats['avg_score']:.1f}/40",
                    f"{stats['pass_rate']:.1f}%",
                    f"{stats['avg_dim_a']:.1f}/10",
                    f"{stats['avg_dim_b']:.1f}/10",
                    f"{stats['avg_dim_c']:.1f}/10",
                    f"{stats['avg_dim_d']:.1f}/10"
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Detailed scores sheet
            detailed_data = []
            for result in results:
                detailed_data.append({
                    'Test ID': result.test_case_id,
                    'Test Name': result.test_name,
                    'Category': result.category,
                    'Dim A': result.dimension_a_score,
                    'Dim B': result.dimension_b_score,
                    'Dim C': result.dimension_c_score,
                    'Dim D': result.dimension_d_score,
                    'Total': result.total_score,
                    'Percentage': result.total_score/40*100,
                    'Status': 'Pass' if result.total_score >= 28 else 'Fail'
                })
            detailed_df = pd.DataFrame(detailed_data)
            detailed_df.to_excel(writer, sheet_name='Detailed Scores', index=False)

            # Per-category sheets
            categories = set(r.category for r in results)
            for category in categories:
                cat_results = [r for r in results if r.category == category]
                cat_data = []
                for result in cat_results:
                    cat_data.append({
                        'Test ID': result.test_case_id,
                        'Test Name': result.test_name,
                        'Dim A': result.dimension_a_score,
                        'Dim B': result.dimension_b_score,
                        'Dim C': result.dimension_c_score,
                        'Dim D': result.dimension_d_score,
                        'Total': result.total_score
                    })
                cat_df = pd.DataFrame(cat_data)
                # Truncate sheet name if too long
                sheet_name = category[:31] if len(category) > 31 else category
                cat_df.to_excel(writer, sheet_name=sheet_name, index=False)

        return excel_path

    def _calculate_statistics(self, results: List) -> dict:
        """Calculate statistics from results"""
        if not results:
            return {}

        total_tests = len(results)
        total_score = sum(r.total_score for r in results)
        avg_score = total_score / total_tests

        # Dimension averages
        avg_dim_a = sum(r.dimension_a_score for r in results) / total_tests
        avg_dim_b = sum(r.dimension_b_score for r in results) / total_tests
        avg_dim_c = sum(r.dimension_c_score for r in results) / total_tests
        avg_dim_d = sum(r.dimension_d_score for r in results) / total_tests

        # Pass rate
        passed = sum(1 for r in results if r.total_score >= 28)
        pass_rate = (passed / total_tests) * 100

        # By category
        by_category = {}
        categories = set(r.category for r in results)
        for category in categories:
            cat_results = [r for r in results if r.category == category]
            cat_total = sum(r.total_score for r in cat_results)
            cat_avg = cat_total / len(cat_results)

            best = max(cat_results, key=lambda x: x.total_score)
            worst = min(cat_results, key=lambda x: x.total_score)

            by_category[category] = {
                'count': len(cat_results),
                'avg_score': cat_avg,
                'avg_percentage': (cat_avg / 40) * 100,
                'best': {'id': best.test_case_id, 'score': best.total_score},
                'worst': {'id': worst.test_case_id, 'score': worst.total_score}
            }

        return {
            'total_tests': total_tests,
            'avg_score': avg_score,
            'avg_percentage': (avg_score / 40) * 100,
            'pass_rate': pass_rate,
            'avg_dim_a': avg_dim_a,
            'avg_dim_b': avg_dim_b,
            'avg_dim_c': avg_dim_c,
            'avg_dim_d': avg_dim_d,
            'by_category': by_category
        }

    def _find_weakest_dimension(self, result) -> str:
        """Find the weakest dimension for a test result"""
        dimensions = {
            'User Requirements': result.dimension_a_score,
            'Target Users': result.dimension_b_score,
            'Market Analysis': result.dimension_c_score,
            'Market Insights': result.dimension_d_score
        }
        weakest = min(dimensions.items(), key=lambda x: x[1])
        return f"{weakest[0]} ({weakest[1]}/10)"


if __name__ == "__main__":
    # Test the report generator with mock data
    from llm_scorer import TestScore

    print("Testing Report Generator...")
    print("=" * 80)

    # Create mock results
    mock_results = [
        TestScore(
            test_case_id="1.1",
            test_name="AI Customer Support Agent",
            category="AI Agent",
            dimension_a_score=7,
            dimension_a_reasoning="Good understanding of requirements",
            dimension_b_score=10,
            dimension_b_reasoning="Excellent user segment definition",
            dimension_c_score=7,
            dimension_c_reasoning="Identified most competitors",
            dimension_d_score=8,
            dimension_d_reasoning="Strong positioning strategies",
            total_score=32,
            execution_time=5.2
        ),
        TestScore(
            test_case_id="1.2",
            test_name="AI Sales Qualification Agent",
            category="AI Agent",
            dimension_a_score=10,
            dimension_a_reasoning="Comprehensive requirements analysis",
            dimension_b_score=7,
            dimension_b_reasoning="Good user identification",
            dimension_c_score=10,
            dimension_c_reasoning="Complete competitor analysis",
            dimension_d_score=7,
            dimension_d_reasoning="Solid market insights",
            total_score=34,
            execution_time=4.8
        )
    ]

    # Generate reports
    generator = ReportGenerator()
    generator.generate_all_reports(mock_results)

    print("\n✓ Test complete! Check test_results/ directory")
