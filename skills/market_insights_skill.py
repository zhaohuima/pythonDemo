"""
Market Insights Skill

Extracts strategic market insights and recommendations.
Focuses on Dimension D of product research.
Loads prompt from Markdown file for easy maintenance.
"""

from .base_skill import BaseSkill
from .prompt_loader import load_prompt_template, format_prompt


class MarketInsightsSkill(BaseSkill):
    """
    市场洞察 Skill | Market Insights Skill

    专注于提取战略性市场洞察和建议，从 Markdown 文件加载 prompt
    Focuses on extracting strategic market insights and recommendations, loads prompt from Markdown file
    """

    PROMPT_FILE = "market_insights.md"

    def get_output_key(self) -> str:
        return "market_insights"

    def get_prompt(self, user_input: str) -> str:
        template = load_prompt_template(self.PROMPT_FILE)
        return format_prompt(template, user_input=user_input)
