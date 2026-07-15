"""Skill repository layer.

Provides database access operations for skills and candidate skills.
"""

from typing import Type

from app.database.models.candidate_skill import CandidateSkill
from app.database.models.skill import Skill
from app.database.repositories.base import BaseRepository


class SkillRepository(
    BaseRepository[Skill, Type[dict], Type[dict]]
):
    """Repository for Skill model."""
    pass


class CandidateSkillRepository(
    BaseRepository[CandidateSkill, Type[dict], Type[dict]]
):
    """Repository for CandidateSkill model."""
    pass
