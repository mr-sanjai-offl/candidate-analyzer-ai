"""Skill Extraction Engine.

Extracts technical skills and attributes from various candidate profiles
deterministically and maps them using standard alias normalizations.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any

from app.database.models.enums import EvidenceSource, SkillCategory

logger = logging.getLogger(__name__)

# Normalization maps
ALIAS_MAP = {
    "fastapi": "Python Backend",
    "flask": "Python Backend",
    "django": "Python Backend",
    "c++": "C++",
    "cpp": "C++",
    "js": "Node.js",
    "javascript": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "docker compose": "Docker",
    "docker": "Docker",
}

# Standardized category mapping for common technologies
CATEGORY_MAP = {
    "python": SkillCategory.LANGUAGE,
    "python backend": SkillCategory.FRAMEWORK,
    "c++": SkillCategory.LANGUAGE,
    "node.js": SkillCategory.FRAMEWORK,
    "docker": SkillCategory.TOOL,
    "postgresql": SkillCategory.DATABASE,
    "mongodb": SkillCategory.DATABASE,
    "mysql": SkillCategory.DATABASE,
    "redis": SkillCategory.DATABASE,
    "aws": SkillCategory.CLOUD,
    "azure": SkillCategory.CLOUD,
    "gcp": SkillCategory.CLOUD,
    "kubernetes": SkillCategory.TOOL,
    "git": SkillCategory.TOOL,
    "react": SkillCategory.FRAMEWORK,
    "angular": SkillCategory.FRAMEWORK,
    "vue": SkillCategory.FRAMEWORK,
    "typescript": SkillCategory.LANGUAGE,
    "rust": SkillCategory.LANGUAGE,
    "go": SkillCategory.LANGUAGE,
    "java": SkillCategory.LANGUAGE,
    "html": SkillCategory.LANGUAGE,
    "css": SkillCategory.LANGUAGE,
}

# Grouping categories into Phase 10 extraction types
EXTRACTION_CATEGORIES = {
    "Programming Languages": [SkillCategory.LANGUAGE],
    "Frameworks": [SkillCategory.FRAMEWORK],
    "Libraries": [SkillCategory.OTHER],
    "Databases": [SkillCategory.DATABASE],
    "Cloud Platforms": [SkillCategory.CLOUD],
    "DevOps": [SkillCategory.TOOL],
    "Containers": [SkillCategory.TOOL],
    "Operating Systems": [SkillCategory.OTHER],
    "Networking": [SkillCategory.OTHER],
    "Cybersecurity": [SkillCategory.OTHER],
    "AI/ML": [SkillCategory.PARADIGM],
    "Embedded Systems": [SkillCategory.OTHER],
    "Mobile": [SkillCategory.OTHER],
    "Frontend": [SkillCategory.FRAMEWORK, SkillCategory.LANGUAGE],
    "Backend": [SkillCategory.FRAMEWORK, SkillCategory.LANGUAGE],
    "Testing": [SkillCategory.TOOL],
    "CI/CD": [SkillCategory.TOOL],
    "Architecture": [SkillCategory.PARADIGM],
    "System Design": [SkillCategory.PARADIGM],
    "Soft Skills": [SkillCategory.OTHER],
    "Certifications": [SkillCategory.OTHER],
}


class SkillExtractionEngine:
    """Deterministic, rule-based skill extraction and alias normalization engine."""

    def __init__(self) -> None:
        self.alias_map = ALIAS_MAP
        self.category_map = CATEGORY_MAP

    def normalize_name(self, name: str) -> str:
        """Standardize a technology name based on alias mappings."""
        cleaned = name.strip().lower()
        # Direct alias lookup
        if cleaned in self.alias_map:
            return self.alias_map[cleaned]
        # Regex cleanups (e.g. "c++17" -> "C++")
        if cleaned.startswith("c++") or cleaned.startswith("cpp"):
            return "C++"
        return name.strip()

    def resolve_category(self, standard_name: str) -> SkillCategory:
        """Infer the SkillCategory for a standardized technology name."""
        cleaned = standard_name.lower()
        return self.category_map.get(cleaned, SkillCategory.OTHER)

    def extract_skills(
        self,
        resume_data: dict[str, Any] | None = None,
        github_profile: dict[str, Any] | None = None,
        leetcode_profile: dict[str, Any] | None = None,
        codeforces_profile: dict[str, Any] | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Run deterministic skill extraction across all platforms profiles.

        Returns a dictionary of skills mapped to their standard names and associated evidence.
        """
        extracted_skills: dict[str, dict[str, Any]] = {}
        now_str = datetime.now(timezone.utc).isoformat()

        def _add_evidence(
            skill_name: str,
            source: EvidenceSource,
            weight: float,
            confidence: int,
            text: str,
            metadata: dict[str, Any] | None = None,
        ) -> None:
            standard_name = self.normalize_name(skill_name)
            category = self.resolve_category(standard_name)

            if standard_name not in extracted_skills:
                extracted_skills[standard_name] = {
                    "name": standard_name,
                    "category": category,
                    "evidences": [],
                }

            # Check if identical evidence source is already logged
            for ev in extracted_skills[standard_name]["evidences"]:
                if ev["source"] == source and ev["evidence"] == text:
                    return

            extracted_skills[standard_name]["evidences"].append({
                "source": source,
                "weight": weight,
                "confidence": confidence,
                "evidence": text,
                "timestamp": now_str,
                "verification_state": "CLAIMED" if source == EvidenceSource.RESUME else "VERIFIED",
                "metadata": metadata or {},
            })

        # ── 1. Resume JSON Extraction ─────────────────────────────────────────
        if resume_data:
            # Main skills lists
            for skill in resume_data.get("skills", []):
                if isinstance(skill, str):
                    _add_evidence(
                        skill,
                        EvidenceSource.RESUME,
                        weight=0.2,
                        confidence=60,
                        text=f"Claimed skill in resume: '{skill}'",
                    )
                elif isinstance(skill, dict) and "name" in skill:
                    _add_evidence(
                        skill["name"],
                        EvidenceSource.RESUME,
                        weight=0.3,
                        confidence=70,
                        text=f"Claimed skill in resume under section '{skill.get('category', 'Skills')}'",
                    )

            # Extract from experience text
            for exp in resume_data.get("work_experience", []):
                desc = exp.get("description", "")
                # Scan for common technologies
                for tech in self.category_map.keys():
                    if re.search(r'\b' + re.escape(tech) + r'\b', desc.lower()):
                        _add_evidence(
                            tech,
                            EvidenceSource.PROJECT,
                            weight=0.4,
                            confidence=75,
                            text=f"Mentioned in work experience at {exp.get('company', 'Company')}",
                        )

        # ── 2. GitHub Extraction ──────────────────────────────────────────────
        if github_profile:
            # Primary language of the profile
            prim_lang = github_profile.get("primary_language")
            if prim_lang:
                _add_evidence(
                    prim_lang,
                    EvidenceSource.GITHUB,
                    weight=0.8,
                    confidence=95,
                    text=f"Identified as candidate's primary language on GitHub.",
                )

            # Language breakdown list
            for skill in github_profile.get("skills", []):
                sname = skill.get("name") if isinstance(skill, dict) else str(skill)
                rel = skill.get("relevance_score", 0.5) if isinstance(skill, dict) else 0.5
                if sname:
                    _add_evidence(
                        sname,
                        EvidenceSource.GITHUB,
                        weight=round(float(rel), 2),
                        confidence=90,
                        text=f"Aggregated technology bytes on GitHub repositories.",
                    )

            # Inspect projects/repositories
            for proj in github_profile.get("projects", []):
                pname = proj.get("name", "")
                plang = proj.get("primary_language", "")
                if plang:
                    _add_evidence(
                        plang,
                        EvidenceSource.PROJECT,
                        weight=0.6,
                        confidence=85,
                        text=f"Used as primary language in repository '{pname}' with {proj.get('stars', 0)} stars.",
                        metadata={"stars": proj.get("stars", 0), "is_fork": proj.get("is_fork", False)},
                    )
                for lang in proj.get("languages", []):
                    _add_evidence(
                        lang,
                        EvidenceSource.PROJECT,
                        weight=0.5,
                        confidence=80,
                        text=f"Contributed to code of repository '{pname}'.",
                    )
                for topic in proj.get("topics", []):
                    _add_evidence(
                        topic,
                        EvidenceSource.PROJECT,
                        weight=0.4,
                        confidence=70,
                        text=f"Tagged topic on repository '{pname}'.",
                    )

        # ── 3. LeetCode Extraction ────────────────────────────────────────────
        if leetcode_profile:
            solved = leetcode_profile.get("problems_solved", 0)
            if solved > 0:
                _add_evidence(
                    "Algorithms",
                    EvidenceSource.LEETCODE,
                    weight=0.8,
                    confidence=90,
                    text=f"Solved {solved} algorithms problems on LeetCode.",
                )
                _add_evidence(
                    "Data Structures",
                    EvidenceSource.LEETCODE,
                    weight=0.7,
                    confidence=85,
                    text=f"Demonstrated DSA knowledge through LeetCode solves.",
                )

            # Topic distribution tags
            for topic, count in leetcode_profile.get("topic_distribution", {}).items():
                _add_evidence(
                    topic,
                    EvidenceSource.LEETCODE,
                    weight=min(1.0, count / 20.0),
                    confidence=int(min(100, 50 + count * 2)),
                    text=f"Solved {count} LeetCode problems tagged with '{topic}'.",
                )

        # ── 4. Codeforces Extraction ──────────────────────────────────────────
        if codeforces_profile:
            cf_rating = codeforces_profile.get("rating", 0)
            if cf_rating > 0:
                _add_evidence(
                    "Competitive Programming",
                    EvidenceSource.CODEFORCES,
                    weight=0.9,
                    confidence=95,
                    text=f"Attained a maximum rating of {codeforces_profile.get('max_rating', cf_rating)} on Codeforces.",
                )
                _add_evidence(
                    "Algorithms",
                    EvidenceSource.CODEFORCES,
                    weight=0.8,
                    confidence=90,
                    text=f"Solved Codeforces contest challenges (Rank: {codeforces_profile.get('rank', 'candidate')}).",
                )

            for tag, count in codeforces_profile.get("topic_distribution", {}).items():
                _add_evidence(
                    tag,
                    EvidenceSource.CODEFORCES,
                    weight=min(1.0, count / 15.0),
                    confidence=int(min(100, 60 + count * 3)),
                    text=f"Solved {count} Codeforces tasks tagged with '{tag}'.",
                )

        return extracted_skills
