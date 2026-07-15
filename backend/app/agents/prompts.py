"""Prompt Management Layer.

Provides template rendering, versioning database fetches, variables injection,
and A/B testing split logic.
"""

import logging
import random
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.prompts import PromptTemplate, PromptVersion

logger = logging.getLogger(__name__)

# Default hardcoded fallback templates for Phase 12 stability
DEFAULT_TEMPLATES = {
    "recruiter_report": {
        "system": "You are a Principal Software Architect. Evaluate the technical candidate's capabilities based on evidence.",
        "user": "Candidate ID: {candidate_id}\nResume:\n{resume_text}\nSkills: {skills}\nScores: {scores}\nConduct a full recruiter report evaluation."
    },
    "candidate_feedback": {
        "system": "You are a friendly Senior Developer. Give candidate feedback and technical improvement paths.",
        "user": "Skills: {skills}\nReadiness: {readiness}\nGaps: {gaps}\nProvide recommendations."
    },
    "interview_generation": {
        "system": "You are an Interviewer. Generate questions based on candidate evidence.",
        "user": "Target topics: {topics}\nVerified skills: {skills}\nGenerate questions."
    },
    "resume_review": {
        "system": "You are a Technical Recruiter. Review the candidate resume.",
        "user": "Resume details:\n{resume_text}\nSuggest improvements."
    },
    "project_recommendations": {
        "system": "You are a Technical Lead. Suggest engineering projects to clear skill gaps.",
        "user": "Weak skills: {weak_skills}\nTarget role: {target_role}\nSuggest projects."
    },
    "learning_roadmap": {
        "system": "You are an educator. Design a step-by-step technical learning priority path.",
        "user": "Learning Priorities: {priorities}\nTimeline: {timeline}"
    },
    "skill_explanation": {
        "system": "You are a Staff ML Engineer. Explain a skill performance score.",
        "user": "Skill: {skill_name}\nEvidence checklist: {evidence}"
    },
    "job_matching": {
        "system": "You are a Technical Hiring Manager. Compare the candidate's capabilities against a Job Description.",
        "user": "Job Description:\n{job_description}\nCandidate Profile:\n{candidate_profile}\nRun match assessment."
    }
}


class PromptManager:
    """Manages prompting templates versions, variables loading, and A/B split routing."""

    def __init__(self) -> None:
        self.defaults = DEFAULT_TEMPLATES

    async def get_prompt(
        self,
        db: AsyncSession | None,
        name: str,
        variables: dict[str, Any],
    ) -> tuple[str, str, int]:
        """Fetch system prompt, user prompt, and version number.

        If database session is present and templates exist, uses DB, otherwise falls back to defaults.
        Supports A/B testing logic when enabled in the DB settings.
        """
        system_tmpl = None
        user_tmpl = None
        version_num = 1

        if db and name in self.defaults:
            try:
                # 1. Fetch template settings
                stmt_tmpl = select(PromptTemplate).where(PromptTemplate.name == name)
                res_tmpl = await db.execute(stmt_tmpl)
                tmpl = res_tmpl.scalars().first()

                if tmpl:
                    # 2. Handle A/B split logic
                    target_version = tmpl.active_version
                    if tmpl.ab_testing_enabled:
                        if random.random() > tmpl.ab_split_ratio:
                            # Route to alternative version (active_version + 1)
                            target_version = tmpl.active_version + 1

                    # 3. Fetch version contents
                    stmt_ver = select(PromptVersion).where(
                        PromptVersion.template_name == name,
                        PromptVersion.version_number == target_version,
                    )
                    res_ver = await db.execute(stmt_ver)
                    ver = res_ver.scalars().first()

                    if ver:
                        system_tmpl = ver.system_prompt
                        user_tmpl = ver.user_prompt
                        version_num = ver.version_number
            except Exception as e:
                logger.warning("Could not fetch prompt from DB, using fallbacks: %s", e)

        # Fallback to local hardcoded defaults if not resolved
        if not system_tmpl or not user_tmpl:
            tmpl_data = self.defaults.get(name, self.defaults["recruiter_report"])
            system_tmpl = tmpl_data["system"]
            user_tmpl = tmpl_data["user"]
            version_num = 1

        # Replace variables
        system_prompt = self._render_template(system_tmpl, variables)
        user_prompt = self._render_template(user_tmpl, variables)

        return system_prompt, user_prompt, version_num

    def _render_template(self, text: str, variables: dict[str, Any]) -> str:
        """Replace placeholders in text safely."""
        rendered = text
        for key, val in variables.items():
            placeholder = f"{{{key}}}"
            rendered = rendered.replace(placeholder, str(val))
        return rendered
