#!/usr/bin/env python3
"""
Test Case Loader
Extracts and parses test cases from the PDF document
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import pdfplumber


@dataclass
class StandardAnswer:
    """Standard answer with 4 sections"""
    user_requirements: str = ""
    target_users: str = ""
    market_competitors: str = ""
    market_insights: str = ""


@dataclass
class ScoringRubric:
    """Scoring rubric for 4 dimensions"""
    dimension_a_criteria: Dict[int, str] = field(default_factory=dict)
    dimension_b_criteria: Dict[int, str] = field(default_factory=dict)
    dimension_c_criteria: Dict[int, str] = field(default_factory=dict)
    dimension_d_criteria: Dict[int, str] = field(default_factory=dict)


@dataclass
class TestCase:
    """Test case structure"""
    id: str
    category: str
    name: str
    user_question: str
    standard_answer: StandardAnswer
    scoring_rubric: ScoringRubric


class TestCaseLoader:
    """Loads test cases from PDF document"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def load_test_cases(self) -> List[TestCase]:
        """Load all test cases from PDF"""
        print(f"Loading test cases from: {self.pdf_path}")

        # Extract text from PDF
        full_text = self._extract_pdf_text()

        # Parse test cases
        test_cases = self._parse_test_cases(full_text)

        print(f"Successfully loaded {len(test_cases)} test cases")
        return test_cases

    def _extract_pdf_text(self) -> str:
        """Extract all text from PDF"""
        text_parts = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

        return "\n".join(text_parts)

    def _parse_test_cases(self, text: str) -> List[TestCase]:
        """Parse test cases from extracted text"""
        test_cases = []

        # Pattern to find test case headers
        # Looking for patterns like "Test Case 1.1:", "Test Case 2.3:", etc.
        test_case_pattern = r'Test Case (\d+\.\d+):\s*(.+?)(?=\nTest Case Type:)'

        # Find all test case matches
        matches = list(re.finditer(test_case_pattern, text, re.DOTALL))

        for i, match in enumerate(matches):
            test_id = match.group(1)
            test_name = match.group(2).strip()

            # Extract the full test case content
            start_pos = match.start()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            test_content = text[start_pos:end_pos]

            # Parse the test case
            test_case = self._parse_single_test_case(test_id, test_name, test_content)
            if test_case:
                test_cases.append(test_case)

        return test_cases

    def _parse_single_test_case(self, test_id: str, test_name: str, content: str) -> Optional[TestCase]:
        """Parse a single test case from its content"""
        try:
            # Extract category
            category_match = re.search(r'Test Case Type:\s*(.+?)(?=\n)', content)
            category = category_match.group(1).strip() if category_match else "Unknown"

            # Extract user question
            question_match = re.search(r'User Question:\s*"(.+?)"', content, re.DOTALL)
            user_question = question_match.group(1).strip() if question_match else ""

            # Extract standard answer sections
            standard_answer = self._extract_standard_answer(content)

            # Extract scoring rubric
            scoring_rubric = self._extract_scoring_rubric(content)

            return TestCase(
                id=test_id,
                category=category,
                name=test_name,
                user_question=user_question,
                standard_answer=standard_answer,
                scoring_rubric=scoring_rubric
            )
        except Exception as e:
            print(f"Warning: Failed to parse test case {test_id}: {e}")
            return None

    def _extract_standard_answer(self, content: str) -> StandardAnswer:
        """Extract standard answer sections"""
        answer = StandardAnswer()

        # Extract User Requirements Analysis
        req_match = re.search(
            r'User Requirements Analysis:\s*(.+?)(?=Target Users:|Market Competitors:|Market Insights:|Scoring Rubric:)',
            content, re.DOTALL
        )
        if req_match:
            answer.user_requirements = req_match.group(1).strip()

        # Extract Target Users
        users_match = re.search(
            r'Target Users:\s*(.+?)(?=Market Competitors:|Market Insights:|Scoring Rubric:)',
            content, re.DOTALL
        )
        if users_match:
            answer.target_users = users_match.group(1).strip()

        # Extract Market Competitors
        competitors_match = re.search(
            r'Market Competitors:\s*(.+?)(?=Market Insights:|Scoring Rubric:)',
            content, re.DOTALL
        )
        if competitors_match:
            answer.market_competitors = competitors_match.group(1).strip()

        # Extract Market Insights
        insights_match = re.search(
            r'Market Insights:\s*(.+?)(?=Scoring Rubric:|Test Case \d+\.\d+:|$)',
            content, re.DOTALL
        )
        if insights_match:
            answer.market_insights = insights_match.group(1).strip()

        return answer

    def _extract_scoring_rubric(self, content: str) -> ScoringRubric:
        """Extract scoring rubric criteria"""
        rubric = ScoringRubric()

        # Extract Scoring Rubric section
        rubric_match = re.search(
            r'Scoring Rubric:\s*(.+?)(?=Test Case \d+\.\d+:|$)',
            content, re.DOTALL
        )

        if not rubric_match:
            return rubric

        rubric_text = rubric_match.group(1)

        # Extract criteria for each dimension
        rubric.dimension_a_criteria = self._extract_dimension_criteria(rubric_text, "User Requirements")
        rubric.dimension_b_criteria = self._extract_dimension_criteria(rubric_text, "Target Users")
        rubric.dimension_c_criteria = self._extract_dimension_criteria(rubric_text, "Market Analysis")
        rubric.dimension_d_criteria = self._extract_dimension_criteria(rubric_text, "Market Insights")

        return rubric

    def _extract_dimension_criteria(self, rubric_text: str, dimension_name: str) -> Dict[int, str]:
        """Extract criteria for a specific dimension"""
        criteria = {}

        # Find the dimension section
        dimension_pattern = rf'{dimension_name}\s*\(10 pts\):\s*(.+?)(?=\n[A-Z][a-z]+ [A-Z][a-z]+.*?\(10 pts\):|$)'
        dimension_match = re.search(dimension_pattern, rubric_text, re.DOTALL)

        if not dimension_match:
            return criteria

        dimension_text = dimension_match.group(1)

        # Extract criteria for each score level
        for score in [10, 7, 4, 1]:
            score_pattern = rf'{score}\s*[=:]\s*(.+?)(?=\d+\s*[=:]|$)'
            score_match = re.search(score_pattern, dimension_text, re.DOTALL)
            if score_match:
                criteria[score] = score_match.group(1).strip()

        return criteria


def load_test_cases_from_pdf(pdf_path: str) -> List[TestCase]:
    """Convenience function to load test cases"""
    loader = TestCaseLoader(pdf_path)
    return loader.load_test_cases()


if __name__ == "__main__":
    # Test the loader
    import sys

    pdf_path = "Product Master Test Case-User and market Research.pdf"
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]

    test_cases = load_test_cases_from_pdf(pdf_path)

    print(f"\nLoaded {len(test_cases)} test cases:")
    for tc in test_cases:
        print(f"  - {tc.id}: {tc.name} ({tc.category})")
