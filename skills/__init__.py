"""
Product Researcher Skills Module

This module contains specialized skills for parallel product research:
- CoreRequirementsSkill: Analyzes explicit and implicit requirements
- TargetUsersSkill: Identifies target user segments and personas
- MarketAnalysisSkill: Conducts competitive market analysis
- MarketInsightsSkill: Extracts strategic market insights

Usage:
    from skills.parallel_orchestrator import ParallelSkillOrchestrator

    orchestrator = ParallelSkillOrchestrator(llm)
    result = await orchestrator.research(user_input)
"""

from .base_skill import BaseSkill
from .core_requirements_skill import CoreRequirementsSkill
from .target_users_skill import TargetUsersSkill
from .market_analysis_skill import MarketAnalysisSkill
from .market_insights_skill import MarketInsightsSkill
from .parallel_orchestrator import ParallelSkillOrchestrator

__all__ = [
    "BaseSkill",
    "CoreRequirementsSkill",
    "TargetUsersSkill",
    "MarketAnalysisSkill",
    "MarketInsightsSkill",
    "ParallelSkillOrchestrator",
]
