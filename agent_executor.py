#!/usr/bin/env python3
"""
Agent Executor
Executes the Product Researcher agent for each test case
"""

import time
from dataclasses import dataclass
from typing import Optional
from agents import ProductResearcher, init_llm


@dataclass
class AgentOutput:
    """Agent execution output"""
    test_case_id: str
    user_requirements: str
    target_users: str
    market_competitors: str
    market_insights: str
    execution_time: float
    status: str  # "success", "error", "timeout"
    error_message: Optional[str] = None


class AgentExecutor:
    """Executes the Product Researcher agent"""

    def __init__(self, timeout: int = 120):
        """
        Initialize agent executor

        Args:
            timeout: Maximum execution time in seconds (default: 120)
        """
        self.timeout = timeout
        self.llm = None
        self.researcher = None

    def _initialize_agent(self):
        """Initialize the agent if not already initialized"""
        if self.researcher is None:
            print("  Initializing Product Researcher agent...")
            self.llm = init_llm()
            self.researcher = ProductResearcher(self.llm)

    def execute_agent(self, test_case) -> AgentOutput:
        """
        Execute the agent for a test case

        Args:
            test_case: TestCase object with user_question

        Returns:
            AgentOutput with results or error
        """
        start_time = time.time()

        try:
            # Initialize agent if needed
            self._initialize_agent()

            # Execute the research
            print(f"  Executing agent for test case {test_case.id}...")
            result = self.researcher.research(test_case.user_question)

            execution_time = time.time() - start_time

            # Check if execution was successful
            if result.get("status") == "completed":
                research_result = result.get("research_result", {})

                return AgentOutput(
                    test_case_id=test_case.id,
                    user_requirements=research_result.get("core_requirements", ""),
                    target_users=research_result.get("target_users", ""),
                    market_competitors=research_result.get("market_analysis", ""),
                    market_insights=research_result.get("market_insights", ""),
                    execution_time=execution_time,
                    status="success"
                )
            else:
                return AgentOutput(
                    test_case_id=test_case.id,
                    user_requirements="",
                    target_users="",
                    market_competitors="",
                    market_insights="",
                    execution_time=execution_time,
                    status="error",
                    error_message="Agent did not complete successfully"
                )

        except TimeoutError:
            execution_time = time.time() - start_time
            return AgentOutput(
                test_case_id=test_case.id,
                user_requirements="",
                target_users="",
                market_competitors="",
                market_insights="",
                execution_time=execution_time,
                status="timeout",
                error_message=f"Execution exceeded {self.timeout} seconds"
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return AgentOutput(
                test_case_id=test_case.id,
                user_requirements="",
                target_users="",
                market_competitors="",
                market_insights="",
                execution_time=execution_time,
                status="error",
                error_message=str(e)
            )


if __name__ == "__main__":
    # Test the executor
    from test_case_loader import load_test_cases_from_pdf

    print("Testing Agent Executor...")
    print("=" * 80)

    # Load test cases
    test_cases = load_test_cases_from_pdf("Product Master Test Case-User and market Research.pdf")

    if test_cases:
        # Test with first test case
        test_case = test_cases[0]
        print(f"\nTesting with: {test_case.id} - {test_case.name}")
        print(f"Question: {test_case.user_question[:100]}...")

        # Execute agent
        executor = AgentExecutor()
        output = executor.execute_agent(test_case)

        print(f"\nStatus: {output.status}")
        print(f"Execution time: {output.execution_time:.2f}s")

        if output.status == "success":
            print(f"\nUser Requirements (first 200 chars):")
            print(output.user_requirements[:200])
            print(f"\nTarget Users (first 200 chars):")
            print(output.target_users[:200])
        else:
            print(f"Error: {output.error_message}")
