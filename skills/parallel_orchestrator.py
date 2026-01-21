"""
Parallel Skill Orchestrator

Orchestrates parallel execution of all product research skills.
Uses asyncio.gather for concurrent API calls.
"""

import asyncio
import logging
from typing import Dict, Any, List

from .core_requirements_skill import CoreRequirementsSkill
from .target_users_skill import TargetUsersSkill
from .market_analysis_skill import MarketAnalysisSkill
from .market_insights_skill import MarketInsightsSkill

logger = logging.getLogger(__name__)


class ParallelSkillOrchestrator:
    """
    并行执行 4 个 Skill 并聚合结果 | Execute 4 Skills in parallel and aggregate results

    使用 asyncio.gather 实现并行调用，显著降低延迟
    Uses asyncio.gather for parallel calls, significantly reducing latency
    """

    def __init__(self, llm):
        """
        初始化编排器 | Initialize orchestrator

        Args:
            llm: 语言模型实例，需要支持 ainvoke 异步方法
                 Language model instance, must support ainvoke async method
        """
        self.llm = llm
        self.skills = [
            CoreRequirementsSkill(llm),
            TargetUsersSkill(llm),
            MarketAnalysisSkill(llm),
            MarketInsightsSkill(llm),
        ]

    def _normalize_line_breaks(self, text: str) -> str:
        """
        将字面字符串 \\n 转换为实际换行符
        Convert literal string \\n to actual line breaks

        Args:
            text: 输入文本 | Input text

        Returns:
            str: 转换后的文本 | Converted text
        """
        if not isinstance(text, str):
            return text
        # 将字面字符串 \n 替换为实际换行符
        return text.replace('\\n', '\n')

    async def research(self, user_input: str) -> Dict[str, Any]:
        """
        并行执行所有 Skill | Execute all Skills in parallel

        Args:
            user_input: 用户输入的产品需求 | User's product requirement input

        Returns:
            Dict[str, Any]: 包含所有维度分析结果的字典
                           Dictionary containing analysis results from all dimensions
        """
        logger.info(f"Starting parallel research with {len(self.skills)} skills")

        # 创建所有 skill 的异步任务
        tasks = [skill.analyze(user_input) for skill in self.skills]

        # 并行执行所有任务，允许部分失败
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 聚合结果，处理失败的 skill
        final_result = {}
        for skill, result in zip(self.skills, results):
            if isinstance(result, Exception):
                logger.warning(f"Skill {skill.name} failed: {result}")
                final_result[skill.get_output_key()] = "Analysis unavailable due to error"
            else:
                # 后处理：转换换行符
                for key, value in result.items():
                    final_result[key] = self._normalize_line_breaks(value)
                logger.info(f"Skill {skill.name} completed successfully")

        logger.info(f"Parallel research completed. Successful: {len([r for r in results if not isinstance(r, Exception)])}/{len(self.skills)}")

        return final_result

    async def research_with_timeout(self, user_input: str, timeout: float = 120.0) -> Dict[str, Any]:
        """
        带超时的并行执行 | Parallel execution with timeout

        Args:
            user_input: 用户输入的产品需求 | User's product requirement input
            timeout: 超时时间（秒）| Timeout in seconds

        Returns:
            Dict[str, Any]: 包含所有维度分析结果的字典
                           Dictionary containing analysis results from all dimensions
        """
        try:
            return await asyncio.wait_for(self.research(user_input), timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(f"Parallel research timed out after {timeout} seconds")
            return {
                "core_requirements": "Analysis timed out",
                "target_users": "Analysis timed out",
                "market_analysis": "Analysis timed out",
                "market_insights": "Analysis timed out",
            }
