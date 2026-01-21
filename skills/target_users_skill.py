"""
Target Users Skill

Identifies and analyzes target user segments and personas.
Focuses on Dimension B of product research.
Loads prompt from Markdown file for easy maintenance.
"""

from .base_skill import BaseSkill
from .prompt_loader import load_prompt_template, format_prompt


class TargetUsersSkill(BaseSkill):
    """
    目标用户 Skill | Target Users Analysis Skill

    专注于识别目标用户群体和用户画像，从 Markdown 文件加载 prompt
    Focuses on identifying target user segments and personas, loads prompt from Markdown file
    """

    PROMPT_FILE = "target_users.md"

    def get_output_key(self) -> str:
        return "target_users"

    def get_prompt(self, user_input: str) -> str:
        template = load_prompt_template(self.PROMPT_FILE)
        return format_prompt(template, user_input=user_input)
