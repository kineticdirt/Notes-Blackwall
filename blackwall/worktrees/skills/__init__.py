"""
Skills system: Nested markdown files for defining agent capabilities.
Based on whiteboard: "Resources -> Points to the nested markdown + DB for UI and Task Comp"
"""

from .skill_loader import SkillLoader, SkillRegistry
from .skill import Skill

__all__ = ['SkillLoader', 'SkillRegistry', 'Skill']
