"""
Prompt Loader

Loads prompt templates from Markdown files in the prompts/ directory.
This enables separation of prompt content from execution logic.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Prompts directory path
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt_template(filename: str) -> str:
    """
    从 prompts 目录加载 Markdown 格式的 prompt 模板
    Load Markdown prompt template from prompts directory

    Args:
        filename: prompt 文件名，如 'core_requirements.md'
                  Prompt filename, e.g., 'core_requirements.md'

    Returns:
        str: prompt 模板内容 | Prompt template content

    Raises:
        FileNotFoundError: 如果文件不存在 | If file does not exist
    """
    filepath = PROMPTS_DIR / filename

    if not filepath.exists():
        logger.error(f"Prompt template not found: {filepath}")
        raise FileNotFoundError(f"Prompt template not found: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    logger.debug(f"Loaded prompt template: {filename} ({len(content)} chars)")
    return content


def format_prompt(template: str, **kwargs) -> str:
    """
    格式化 prompt 模板，替换占位符
    Format prompt template, replacing placeholders

    Args:
        template: prompt 模板 | Prompt template
        **kwargs: 占位符替换值 | Placeholder replacement values

    Returns:
        str: 格式化后的 prompt | Formatted prompt
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        logger.error(f"Missing placeholder in prompt template: {e}")
        raise ValueError(f"Missing placeholder in prompt template: {e}")


def get_available_prompts() -> list:
    """
    获取所有可用的 prompt 模板文件
    Get all available prompt template files

    Returns:
        list: prompt 文件名列表 | List of prompt filenames
    """
    if not PROMPTS_DIR.exists():
        return []

    return [f.name for f in PROMPTS_DIR.glob("*.md")]
