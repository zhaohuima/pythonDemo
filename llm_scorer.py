#!/usr/bin/env python3
"""
LLM Scorer
Uses SiliconFlow Seed-OSS-36B-Instruct to score agent outputs
"""

import json
import time
import requests
from dataclasses import dataclass
from typing import Dict, Optional
import config


@dataclass
class TestScore:
    """Test score with all 4 dimensions"""
    test_case_id: str
    test_name: str
    category: str
    dimension_a_score: int
    dimension_a_reasoning: str
    dimension_b_score: int
    dimension_b_reasoning: str
    dimension_c_score: int
    dimension_c_reasoning: str
    dimension_d_score: int
    dimension_d_reasoning: str
    total_score: int
    execution_time: float
    scorer_model: str = ""  # Model used for scoring
    # Additional fields for detailed reporting
    user_question: str = ""
    agent_user_requirements: str = ""
    agent_target_users: str = ""
    agent_market_competitors: str = ""
    agent_market_insights: str = ""


class LLMScorer:
    """Scores agent outputs using LLM"""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        Initialize LLM scorer

        Args:
            api_key: SiliconFlow API key (default: from config)
            base_url: API base URL (default: from config)
            model: Model name (default: ByteDance-Seed/Seed-OSS-36B-Instruct for scoring)
        """
        self.api_key = api_key or config.API_KEY
        self.base_url = base_url or config.API_BASE_URL
        # Use ByteDance-Seed/Seed-OSS-36B-Instruct for scoring (different from main system)
        self.model = model or "ByteDance-Seed/Seed-OSS-36B-Instruct"
        self.temperature = 0.1  # Low temperature for consistent scoring

    def score_output(self, agent_output, test_case) -> TestScore:
        """
        Score agent output against test case

        Args:
            agent_output: AgentOutput object
            test_case: TestCase object with standard answer and rubric

        Returns:
            TestScore with all dimension scores
        """
        start_time = time.time()

        print(f"  Scoring output for test case {test_case.id}...")

        # Score each dimension
        dim_a_score, dim_a_reasoning = self._score_dimension(
            "User Requirements",
            agent_output.user_requirements,
            test_case.standard_answer.user_requirements,
            test_case.scoring_rubric.dimension_a_criteria
        )

        dim_b_score, dim_b_reasoning = self._score_dimension(
            "Target Users",
            agent_output.target_users,
            test_case.standard_answer.target_users,
            test_case.scoring_rubric.dimension_b_criteria
        )

        dim_c_score, dim_c_reasoning = self._score_dimension(
            "Market Analysis",
            agent_output.market_competitors,
            test_case.standard_answer.market_competitors,
            test_case.scoring_rubric.dimension_c_criteria
        )

        dim_d_score, dim_d_reasoning = self._score_dimension(
            "Market Insights",
            agent_output.market_insights,
            test_case.standard_answer.market_insights,
            test_case.scoring_rubric.dimension_d_criteria
        )

        total_score = dim_a_score + dim_b_score + dim_c_score + dim_d_score
        execution_time = time.time() - start_time

        return TestScore(
            test_case_id=test_case.id,
            test_name=test_case.name,
            category=test_case.category,
            dimension_a_score=dim_a_score,
            dimension_a_reasoning=dim_a_reasoning,
            dimension_b_score=dim_b_score,
            dimension_b_reasoning=dim_b_reasoning,
            dimension_c_score=dim_c_score,
            dimension_c_reasoning=dim_c_reasoning,
            dimension_d_score=dim_d_score,
            dimension_d_reasoning=dim_d_reasoning,
            total_score=total_score,
            execution_time=execution_time,
            scorer_model=self.model,  # Add scorer model information
            # Add test case and agent output details
            user_question=test_case.user_question,
            agent_user_requirements=agent_output.user_requirements,
            agent_target_users=agent_output.target_users,
            agent_market_competitors=agent_output.market_competitors,
            agent_market_insights=agent_output.market_insights
        )

    def _score_dimension(
        self,
        dimension_name: str,
        agent_output: str,
        standard_answer: str,
        criteria: Dict[int, str]
    ) -> tuple[int, str]:
        """
        Score a single dimension

        Args:
            dimension_name: Name of the dimension
            agent_output: Agent's output for this dimension
            standard_answer: Standard answer for this dimension
            criteria: Scoring criteria dict {10: "...", 7: "...", 4: "...", 1: "..."}

        Returns:
            Tuple of (score, reasoning)
        """
        # Construct scoring prompt
        prompt = self._build_scoring_prompt(
            dimension_name,
            agent_output,
            standard_answer,
            criteria
        )

        # Call LLM API
        try:
            response = self._call_llm_api(prompt)
            score, reasoning = self._parse_score_response(response)

            # Validate score
            if score not in [1, 4, 7, 10]:
                print(f"    Warning: Invalid score {score} for {dimension_name}, defaulting to 4")
                score = 4

            return score, reasoning

        except Exception as e:
            print(f"    Error scoring {dimension_name}: {e}")
            return 4, f"Error during scoring: {str(e)}"

    def _build_scoring_prompt(
        self,
        dimension_name: str,
        agent_output: str,
        standard_answer: str,
        criteria: Dict[int, str]
    ) -> str:
        """Build the scoring prompt"""
        prompt = f"""You are an expert evaluator for Product Manager Agent outputs.

TASK: Score the agent's response for Dimension "{dimension_name}" on a scale of 1, 4, 7, or 10 points.

AGENT'S OUTPUT:
{agent_output}

STANDARD ANSWER (for reference):
{standard_answer}

SCORING CRITERIA:
- 10 points: {criteria.get(10, "Excellent - meets all requirements")}
- 7 points: {criteria.get(7, "Good - meets most requirements")}
- 4 points: {criteria.get(4, "Fair - meets some requirements")}
- 1 point: {criteria.get(1, "Poor - does not meet requirements")}

Provide your evaluation in JSON format:
{{
  "score": <1, 4, 7, or 10>,
  "reasoning": "<brief explanation of why this score was assigned>"
}}

IMPORTANT: You must respond with ONLY valid JSON. Do not include any other text."""

        return prompt

    def _call_llm_api(self, prompt: str, max_retries: int = 3) -> str:
        """
        Call SiliconFlow API

        Args:
            prompt: The prompt to send
            max_retries: Maximum number of retries

        Returns:
            API response text
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": 500
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=90)
                response.raise_for_status()

                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return content

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"    API call failed, retrying in {wait_time}s... ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"API call failed after {max_retries} attempts: {e}")

    def _parse_score_response(self, response: str) -> tuple[int, str]:
        """
        Parse the LLM response to extract score and reasoning

        Args:
            response: LLM response text

        Returns:
            Tuple of (score, reasoning)
        """
        try:
            # Try to parse as JSON
            data = json.loads(response)
            score = int(data.get("score", 4))
            reasoning = data.get("reasoning", "No reasoning provided")
            return score, reasoning

        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.+?\})\s*```', response, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    score = int(data.get("score", 4))
                    reasoning = data.get("reasoning", "No reasoning provided")
                    return score, reasoning
                except:
                    pass

            # Try to find score and reasoning in text
            score_match = re.search(r'"score":\s*(\d+)', response)
            reasoning_match = re.search(r'"reasoning":\s*"([^"]+)"', response)

            score = int(score_match.group(1)) if score_match else 4
            reasoning = reasoning_match.group(1) if reasoning_match else "Could not parse reasoning"

            return score, reasoning


if __name__ == "__main__":
    # Test the scorer
    from test_case_loader import load_test_cases_from_pdf
    from agent_executor import AgentExecutor

    print("Testing LLM Scorer...")
    print("=" * 80)

    # Load test cases
    test_cases = load_test_cases_from_pdf("Product Master Test Case-User and market Research.pdf")

    if test_cases:
        # Test with first test case
        test_case = test_cases[0]
        print(f"\nTesting with: {test_case.id} - {test_case.name}")

        # Execute agent
        executor = AgentExecutor()
        agent_output = executor.execute_agent(test_case)

        if agent_output.status == "success":
            # Score output
            scorer = LLMScorer()
            test_score = scorer.score_output(agent_output, test_case)

            print(f"\n{'=' * 80}")
            print(f"SCORING RESULTS")
            print(f"{'=' * 80}")
            print(f"Test Case: {test_score.test_case_id} - {test_score.test_name}")
            print(f"Category: {test_score.category}")
            print(f"\nDimension A (User Requirements): {test_score.dimension_a_score}/10")
            print(f"  Reasoning: {test_score.dimension_a_reasoning}")
            print(f"\nDimension B (Target Users): {test_score.dimension_b_score}/10")
            print(f"  Reasoning: {test_score.dimension_b_reasoning}")
            print(f"\nDimension C (Market Analysis): {test_score.dimension_c_score}/10")
            print(f"  Reasoning: {test_score.dimension_c_reasoning}")
            print(f"\nDimension D (Market Insights): {test_score.dimension_d_score}/10")
            print(f"  Reasoning: {test_score.dimension_d_reasoning}")
            print(f"\nTOTAL SCORE: {test_score.total_score}/40 ({test_score.total_score/40*100:.1f}%)")
            print(f"Scoring time: {test_score.execution_time:.2f}s")
        else:
            print(f"Agent execution failed: {agent_output.error_message}")
