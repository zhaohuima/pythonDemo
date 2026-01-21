"""
Base Skill Class

Abstract base class for all product research skills.
Each skill focuses on a single dimension of product research.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BaseSkill(ABC):
    """
    所有 Skill 的基类 | Base class for all Skills

    每个 Skill 专注于产品研究的一个维度
    Each Skill focuses on a single dimension of product research
    """

    def __init__(self, llm):
        """
        初始化 Skill | Initialize Skill

        Args:
            llm: 语言模型实例，需要支持 ainvoke 异步方法
                 Language model instance, must support ainvoke async method
        """
        self.llm = llm
        self.name = self.__class__.__name__

    @abstractmethod
    def get_prompt(self, user_input: str) -> str:
        """
        返回该 Skill 专用的 prompt | Return the skill-specific prompt

        Args:
            user_input: 用户输入的产品需求 | User's product requirement input

        Returns:
            str: 完整的 prompt 字符串 | Complete prompt string
        """
        pass

    @abstractmethod
    def get_output_key(self) -> str:
        """
        返回输出字段名 | Return the output field name

        Returns:
            str: 输出字段名，如 'core_requirements' | Output field name
        """
        pass

    async def analyze(self, user_input: str) -> Dict[str, Any]:
        """
        执行分析并返回结果 | Execute analysis and return result

        Args:
            user_input: 用户输入的产品需求 | User's product requirement input

        Returns:
            Dict[str, Any]: 包含分析结果的字典 | Dictionary containing analysis result
        """
        logger.info(f"Skill {self.name} starting analysis")

        try:
            prompt = self.get_prompt(user_input)
            response = await self.llm.ainvoke(prompt)

            logger.info(f"Skill {self.name} completed successfully")
            return {self.get_output_key(): response}

        except Exception as e:
            logger.error(f"Skill {self.name} failed: {e}")
            raise
