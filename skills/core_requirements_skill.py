"""
Core Requirements Skill

Analyzes explicit and implicit requirements from user input.
Focuses on Dimension A of product research.
Loads prompt from Markdown file for easy maintenance.
"""

from .base_skill import BaseSkill
from .prompt_loader import load_prompt_template, format_prompt


class CoreRequirementsSkill(BaseSkill):
    """
    需求分析 Skill | Core Requirements Analysis Skill

    专注于分析显式和隐式需求，从 Markdown 文件加载 prompt
    Focuses on analyzing explicit and implicit requirements, loads prompt from Markdown file
    """

    PROMPT_FILE = "core_requirements.md"

    def get_output_key(self) -> str:
        return "core_requirements"

    def get_prompt(self, user_input: str) -> str:
        template = load_prompt_template(self.PROMPT_FILE)
        return format_prompt(template, user_input=user_input)
