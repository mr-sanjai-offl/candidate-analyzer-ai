"""Readiness Assessment Engine.

Computes job readiness percentages (0-100) across 9 engineering profiles
based on deterministic keyword and category scores.
"""

from typing import Any

ROLE_SKILL_REQUIREMENTS = {
    "Backend": {
        "categories": ["Programming Languages", "Frameworks", "Databases", "Algorithms", "Data Structures"],
        "skills": ["python", "java", "go", "c++", "python backend", "node.js", "postgresql", "redis", "mongodb"],
    },
    "Frontend": {
        "categories": ["Programming Languages", "Frameworks"],
        "skills": ["javascript", "typescript", "react", "angular", "vue", "html", "css"],
    },
    "Full Stack": {
        "categories": ["Programming Languages", "Frameworks", "Databases"],
        "skills": ["javascript", "typescript", "react", "python", "python backend", "node.js", "postgresql"],
    },
    "AI Engineer": {
        "categories": ["Programming Languages", "AI", "Machine Learning", "Algorithms"],
        "skills": ["python", "tensorflow", "pytorch", "numpy", "pandas", "scikit-learn"],
    },
    "Data Engineer": {
        "categories": ["Programming Languages", "Databases", "Cloud"],
        "skills": ["python", "postgresql", "mongodb", "redis", "mysql", "spark", "hadoop"],
    },
    "DevOps": {
        "categories": ["DevOps", "Cloud", "Testing", "CI/CD"],
        "skills": ["docker", "kubernetes", "git", "jenkins", "terraform", "ansible"],
    },
    "Cloud": {
        "categories": ["Cloud", "DevOps"],
        "skills": ["aws", "gcp", "azure", "kubernetes", "docker"],
    },
    "Cybersecurity": {
        "categories": ["Security", "Networking", "Programming Languages"],
        "skills": ["linux", "bash", "wireshark", "security", "networking"],
    },
    "Embedded Systems": {
        "categories": ["Programming Languages", "Architecture"],
        "skills": ["c++", "c", "assembly", "microcontrollers", "linux", "operating systems"],
    },
}


class ReadinessAssessmentEngine:
    """Evaluates candidate readiness scores for various target software roles."""

    def __init__(self) -> None:
        self.requirements = ROLE_SKILL_REQUIREMENTS

    def assess_readiness(
        self,
        category_scores: dict[str, dict[str, Any]],
        extracted_skills: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """Compute readiness scores (0-100) and descriptions for each role."""
        results: dict[str, dict[str, Any]] = {}

        for role, reqs in self.requirements.items():
            results[role] = self._assess_role(role, reqs, category_scores, extracted_skills)

        return results

    def _assess_role(
        self,
        role: str,
        reqs: dict[str, list[str]],
        category_scores: dict[str, dict[str, Any]],
        extracted_skills: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Calculate score and gap context for a single job role."""
        # 1. Compute Category Score average
        cat_scores = []
        for cat in reqs["categories"]:
            score_data = category_scores.get(cat, {})
            if score_data and score_data.get("experience_score", 0.0) > 0:
                cat_scores.append(score_data.get("experience_score", 0.0))

        # 2. Check skill matching percentage
        skills_matched = []
        for target_skill in reqs["skills"]:
            if target_skill in extracted_skills:
                skills_matched.append(target_skill)

        skill_match_ratio = len(skills_matched) / len(reqs["skills"]) if reqs["skills"] else 0.0
        avg_cat_score = sum(cat_scores) / len(cat_scores) if cat_scores else 0.0

        # Weighted calculation
        role_score = min(100.0, (avg_cat_score * 0.6) + (skill_match_ratio * 40.0))

        # Generate details
        details = [
            f"Matching {len(skills_matched)} out of {len(reqs['skills'])} target technologies.",
            f"Core score categories performance index: {round(avg_cat_score, 1)}%."
        ]
        
        missing_required = [s for s in reqs["skills"] if s not in extracted_skills]

        return {
            "score": round(role_score, 2),
            "explanation": {
                "summary": f"Assessment score of {round(role_score, 1)}% for '{role}' role.",
                "details": details,
                "missing_skills": missing_required[:5],
                "matched_skills": skills_matched,
            }
        }
