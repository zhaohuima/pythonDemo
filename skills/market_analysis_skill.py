"""
Market Analysis Skill

Conducts competitive market analysis.
Focuses on Dimension C of product research.
Loads prompt from Markdown file for easy maintenance.
"""

from .base_skill import BaseSkill
from .prompt_loader import load_prompt_template, format_prompt


class MarketAnalysisSkill(BaseSkill):
    """
    市场分析 Skill | Market Analysis Skill

    专注于竞争对手分析和市场格局，从 Markdown 文件加载 prompt
    Focuses on competitor analysis and market landscape, loads prompt from Markdown file
    """

    PROMPT_FILE = "market_analysis.md"

    def get_output_key(self) -> str:
        return "market_analysis"

    def get_prompt(self, user_input: str) -> str:
        template = load_prompt_template(self.PROMPT_FILE)
        return format_prompt(template, user_input=user_input)
