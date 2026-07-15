"""Capability Scoring Engine.

Deterministic, mathematical evidence-backed capability scoring engine.
No LLM or AI models are used. All calculations explain why they reached a given score.
"""

import math
from typing import Any

from app.database.models.enums import EvidenceSource, ProficiencyLevel

# 20 required scoring categories
SCORING_CATEGORIES = [
    "Programming Languages", "Frameworks", "Libraries", "Databases", "Cloud",
    "DevOps", "Security", "Networking", "AI", "Machine Learning",
    "Data Structures", "Algorithms", "Problem Solving", "Projects", "Open Source",
    "Architecture", "Testing", "Leadership", "Consistency", "Learning Speed"
]

# Map SkillCategories and skill keywords to scoring categories
TECH_TO_SCORE_CATEGORY = {
    # Programming Languages
    "python": "Programming Languages",
    "c++": "Programming Languages",
    "typescript": "Programming Languages",
    "javascript": "Programming Languages",
    "go": "Programming Languages",
    "rust": "Programming Languages",
    "java": "Programming Languages",
    # Frameworks
    "python backend": "Frameworks",
    "react": "Frameworks",
    "angular": "Frameworks",
    "vue": "Frameworks",
    "node.js": "Frameworks",
    # Databases
    "postgresql": "Databases",
    "mongodb": "Databases",
    "mysql": "Databases",
    "redis": "Databases",
    # Cloud
    "aws": "Cloud",
    "azure": "Cloud",
    "gcp": "Cloud",
    # DevOps / Containers
    "docker": "DevOps",
    "kubernetes": "DevOps",
    "git": "DevOps",
}


class CapabilityScoringEngine:
    """Computes technical category scores based on weighted evidence."""

    def __init__(self) -> None:
        self.categories = SCORING_CATEGORIES
        self.tech_map = TECH_TO_SCORE_CATEGORY

    def compute_category_scores(
        self,
        extracted_skills: dict[str, dict[str, Any]],
        github_metrics: dict[str, Any] | None = None,
        leetcode_metrics: dict[str, Any] | None = None,
        codeforces_metrics: dict[str, Any] | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Calculate score metrics and explanations for all 20 categories."""
        scores: dict[str, dict[str, Any]] = {}

        for category in self.categories:
            category_skills = [
                skill for name, skill in extracted_skills.items()
                if self._match_skill_to_category(name, skill.get("category"), category)
            ]

            scores[category] = self._calculate_scores(
                category=category,
                skills=category_skills,
                github=github_metrics,
                leetcode=leetcode_metrics,
                codeforces=codeforces_metrics,
            )

        return scores

    def _match_skill_to_category(self, name: str, category_enum: Any, target_category: str) -> bool:
        """Link a skill to one or more scoring categories."""
        name_lower = name.lower()
        # Direct lookup mapping
        if self.tech_map.get(name_lower) == target_category:
            return True

        # Fallback category checks
        if target_category == "Programming Languages":
            return str(category_enum) == "LANGUAGE"
        elif target_category == "Frameworks":
            return str(category_enum) == "FRAMEWORK"
        elif target_category == "Databases":
            return str(category_enum) == "DATABASE"
        elif target_category == "Cloud":
            return str(category_enum) == "CLOUD"
        elif target_category == "DevOps":
            return str(category_enum) == "TOOL" and name_lower in ("docker", "kubernetes", "jenkins", "terraform", "ansible", "git")
        elif target_category in ("Data Structures", "Algorithms", "Problem Solving"):
            # Check LeetCode/Codeforces DSA topics
            dsa_keywords = ("dsa", "graph", "tree", "greedy", "sort", "search", "math", "string", "hash", "matrix", "array", "binary search", "recursion", "dynamic programming")
            return name_lower in dsa_keywords or target_category == "Problem Solving" and name_lower == "competitive programming"
        elif target_category == "AI" or target_category == "Machine Learning":
            ai_keywords = ("ai", "machine learning", "ml", "deep learning", "nlp", "tensorflow", "pytorch", "keras", "scikit-learn", "numpy", "pandas")
            return name_lower in ai_keywords
        return False

    def _calculate_scores(
        self,
        category: str,
        skills: list[dict[str, Any]],
        github: dict[str, Any] | None,
        leetcode: dict[str, Any] | None,
        codeforces: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Apply deterministic formula to compute scores for a specific category."""
        all_evidences: list[dict[str, Any]] = []
        for s in skills:
            all_evidences.extend(s.get("evidences", []))

        # Check special categories driven by platform metrics rather than explicit skills
        if category == "Open Source":
            return self._calculate_open_source_score(github, all_evidences)
        elif category == "Consistency":
            return self._calculate_consistency_score(github, leetcode, codeforces)
        elif category == "Learning Speed":
            return self._calculate_learning_speed_score(github, leetcode, codeforces)
        elif category == "Projects":
            return self._calculate_projects_score(github, all_evidences)
        elif category == "Leadership":
            return self._calculate_leadership_score(github, all_evidences)

        # ── 1. Confidence Score ───────────────────────────────────────────────
        # Based on source diversity and confidence levels of the evidence
        if not all_evidences:
            return self._build_empty_score(category)

        total_confidence = sum(e["confidence"] for e in all_evidences)
        avg_confidence = total_confidence / len(all_evidences)

        # Boost confidence based on unique sources
        sources = {e["source"] for e in all_evidences}
        source_boost = min(15.0, (len(sources) - 1) * 7.5)
        confidence_score = min(100.0, avg_confidence + source_boost)

        # ── 2. Experience Score ───────────────────────────────────────────────
        # Logarithmic scale on the total count of evidences and weights
        total_weight = sum(e["weight"] for e in all_evidences)
        experience_score = min(100.0, 15.0 + 35.0 * math.log(total_weight + 1, 2))

        # ── 3. Depth Score ────────────────────────────────────────────────────
        # Based on average weight and peak verification level
        avg_weight = total_weight / len(all_evidences)
        has_verified = any(e["verification_state"] == "VERIFIED" for e in all_evidences)
        depth_base = avg_weight * 70.0
        depth_boost = 30.0 if has_verified else 10.0
        depth_score = min(100.0, depth_base + depth_boost)

        # ── 4. Breadth Score ──────────────────────────────────────────────────
        # Distinct standardized skills in the category
        breadth_score = min(100.0, len(skills) * 20.0)

        # ── 5. Final Proficiency ──────────────────────────────────────────────
        overall_average = (confidence_score + experience_score + depth_score + breadth_score) / 4.0
        if overall_average >= 80.0:
            proficiency = ProficiencyLevel.EXPERT
        elif overall_average >= 55.0:
            proficiency = ProficiencyLevel.ADVANCED
        elif overall_average >= 30.0:
            proficiency = ProficiencyLevel.INTERMEDIATE
        else:
            proficiency = ProficiencyLevel.BEGINNER

        # ── 6. Explanation Generator ─────────────────────────────────────────
        sources_str = ", ".join(sorted(list(sources)))
        explanation = {
            "summary": f"Proficiency evaluated as {proficiency.value} based on {len(all_evidences)} pieces of evidence from: {sources_str}.",
            "details": [
                f"Confidence Score of {round(confidence_score, 1)}% derived from source trust levels and variety.",
                f"Experience Score of {round(experience_score, 1)}% calculated using log weights of verified occurrences.",
                f"Depth Score of {round(depth_score, 1)}% reflects project intensity and verification checks.",
                f"Breadth Score of {round(breadth_score, 1)}% reflects coverage of {len(skills)} distinct skills in {category}."
            ],
            "factors": {
                "evidence_count": len(all_evidences),
                "unique_skills_count": len(skills),
                "verification_ratio": len([e for e in all_evidences if e["verification_state"] == "VERIFIED"]) / len(all_evidences)
            }
        }

        return {
            "category": category,
            "confidence_score": round(confidence_score, 2),
            "experience_score": round(experience_score, 2),
            "depth_score": round(depth_score, 2),
            "breadth_score": round(breadth_score, 2),
            "proficiency": proficiency,
            "explanation": explanation,
        }

    def _build_empty_score(self, category: str) -> dict[str, Any]:
        """Produce placeholder score when no evidence is found."""
        return {
            "category": category,
            "confidence_score": 0.0,
            "experience_score": 0.0,
            "depth_score": 0.0,
            "breadth_score": 0.0,
            "proficiency": ProficiencyLevel.BEGINNER,
            "explanation": {
                "summary": f"No evidence of skills found in the category '{category}'.",
                "details": ["Experience score is 0 due to absence of keywords and repository metadata."],
                "factors": {"evidence_count": 0, "unique_skills_count": 0, "verification_ratio": 0.0}
            }
        }

    # ── Platform-Specific & Hybrid Scoring overrides ────────────────────────

    def _calculate_open_source_score(self, github: dict[str, Any] | None, evidences: list[dict[str, Any]]) -> dict[str, Any]:
        """Evaluate open source contributions using GitHub stats."""
        if not github:
            return self._build_empty_score("Open Source")

        public_repos = github.get("public_repos", 0)
        stars = github.get("total_contributions", 0) or github.get("extra", {}).get("total_stars_received", 0)
        followers = github.get("followers", 0)

        # Deterministic formula
        experience_val = min(100.0, 10.0 + 15.0 * math.log(public_repos + 1, 2))
        depth_val = min(100.0, 20.0 * math.log(stars + 1, 3))
        confidence_val = min(100.0, 50.0 + 10.0 * math.log(followers + 1, 2))
        breadth_val = min(100.0, public_repos * 10.0)

        overall = (experience_val + depth_val + confidence_val + breadth_val) / 4.0
        proficiency = ProficiencyLevel.BEGINNER
        if overall >= 80.0:
            proficiency = ProficiencyLevel.EXPERT
        elif overall >= 55.0:
            proficiency = ProficiencyLevel.ADVANCED
        elif overall >= 30.0:
            proficiency = ProficiencyLevel.INTERMEDIATE

        return {
            "category": "Open Source",
            "confidence_score": round(confidence_val, 2),
            "experience_score": round(experience_val, 2),
            "depth_score": round(depth_val, 2),
            "breadth_score": round(breadth_val, 2),
            "proficiency": proficiency,
            "explanation": {
                "summary": f"Open source capability rated as {proficiency.value} based on GitHub profile parameters.",
                "details": [
                    f"Parsed {public_repos} public repositories contributing to code footprint.",
                    f"Earned {stars} total stars across candidate repositories.",
                    f"Followed by {followers} GitHub users, reinforcing validation trust."
                ],
                "factors": {"public_repos": public_repos, "stars": stars, "followers": followers}
            }
        }

    def _calculate_consistency_score(
        self, github: dict[str, Any] | None, leetcode: dict[str, Any] | None, codeforces: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Evaluate learning and coding consistency across all platforms."""
        github_consistency = github.get("contribution_consistency", 0.0) * 100.0 if github else 0.0
        leetcode_consistency = 60.0 if leetcode and leetcode.get("problems_solved", 0) > 0 else 0.0
        cf_consistency = codeforces.get("contribution_consistency", 0.0) * 100.0 if codeforces else 0.0

        scores = [github_consistency, leetcode_consistency, cf_consistency]
        non_zero = [s for s in scores if s > 0]
        score_val = sum(non_zero) / len(non_zero) if non_zero else 0.0

        proficiency = ProficiencyLevel.BEGINNER
        if score_val >= 80.0:
            proficiency = ProficiencyLevel.EXPERT
        elif score_val >= 55.0:
            proficiency = ProficiencyLevel.ADVANCED
        elif score_val >= 30.0:
            proficiency = ProficiencyLevel.INTERMEDIATE

        return {
            "category": "Consistency",
            "confidence_score": round(score_val, 2),
            "experience_score": round(score_val, 2),
            "depth_score": round(score_val, 2),
            "breadth_score": round(score_val, 2),
            "proficiency": proficiency,
            "explanation": {
                "summary": f"Calculated Consistency score of {round(score_val, 1)}% from activity histories.",
                "details": [
                    f"GitHub commit consistency: {round(github_consistency, 1)}%.",
                    f"LeetCode participation: {round(leetcode_consistency, 1)}%.",
                    f"Codeforces contest activity index: {round(cf_consistency, 1)}%."
                ],
                "factors": {"active_platforms_count": len(non_zero)}
            }
        }

    def _calculate_learning_speed_score(
        self, github: dict[str, Any] | None, leetcode: dict[str, Any] | None, codeforces: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Assess capability to absorb tech stack and concepts using solve rates & repo ages."""
        active_platforms = 0
        solves_factor = 0.0
        if leetcode:
            active_platforms += 1
            solves_factor += min(50.0, leetcode.get("problems_solved", 0) / 5.0)
        if codeforces:
            active_platforms += 1
            solves_factor += min(50.0, codeforces.get("problems_solved", 0) / 4.0)

        # Baseline learning speed calculation
        experience_val = 40.0 + (active_platforms * 15.0)
        depth_val = min(100.0, 30.0 + solves_factor)

        overall = (experience_val + depth_val) / 2.0
        proficiency = ProficiencyLevel.BEGINNER
        if overall >= 80.0:
            proficiency = ProficiencyLevel.EXPERT
        elif overall >= 55.0:
            proficiency = ProficiencyLevel.ADVANCED
        elif overall >= 30.0:
            proficiency = ProficiencyLevel.INTERMEDIATE

        return {
            "category": "Learning Speed",
            "confidence_score": round(experience_val, 2),
            "experience_score": round(experience_val, 2),
            "depth_score": round(depth_val, 2),
            "breadth_score": round(depth_val, 2),
            "proficiency": proficiency,
            "explanation": {
                "summary": f"Learning Speed rated as {proficiency.value} using platform solve counts.",
                "details": [
                    f"Evaluated concept ingestion speed over {active_platforms} competitive platforms.",
                    f"Aggregate learning milestones: {round(solves_factor, 1)}% velocity indicator."
                ],
                "factors": {"active_platforms": active_platforms}
            }
        }

    def _calculate_projects_score(self, github: dict[str, Any] | None, evidences: list[dict[str, Any]]) -> dict[str, Any]:
        """Aggregate evaluation of candidate personal and professional projects."""
        if not github or not github.get("projects"):
            return self._build_empty_score("Projects")

        projects_list = github["projects"]
        count = len(projects_list)
        total_stars = sum(p.get("stars", 0) for p in projects_list)

        experience_val = min(100.0, 20.0 + 20.0 * math.log(count + 1, 2))
        depth_val = min(100.0, 15.0 * math.log(total_stars + 1, 2) + 20.0)

        overall = (experience_val + depth_val) / 2.0
        proficiency = ProficiencyLevel.BEGINNER
        if overall >= 80.0:
            proficiency = ProficiencyLevel.EXPERT
        elif overall >= 55.0:
            proficiency = ProficiencyLevel.ADVANCED
        elif overall >= 30.0:
            proficiency = ProficiencyLevel.INTERMEDIATE

        return {
            "category": "Projects",
            "confidence_score": round(overall, 2),
            "experience_score": round(experience_val, 2),
            "depth_score": round(depth_val, 2),
            "breadth_score": round(experience_val, 2),
            "proficiency": proficiency,
            "explanation": {
                "summary": f"Projects evaluation score is {round(overall, 1)}% based on public repos.",
                "details": [
                    f"Analyzed {count} repositories under active candidate ownership.",
                    f"Accumulated {total_stars} stargazers across repositories."
                ],
                "factors": {"projects_count": count, "total_stars": total_stars}
            }
        }

    def _calculate_leadership_score(self, github: dict[str, Any] | None, evidences: list[dict[str, Any]]) -> dict[str, Any]:
        """Estimate candidate coordination/leadership from followers and resume indicators."""
        followers = github.get("followers", 0) if github else 0
        resume_indicators = len([e for e in evidences if e["source"] == EvidenceSource.RESUME and any(kw in e["evidence"].lower() for kw in ("lead", "manager", "mentor", "coordinator", "senior"))])

        score_val = min(100.0, 10.0 + (resume_indicators * 20.0) + 15.0 * math.log(followers + 1, 2))

        proficiency = ProficiencyLevel.BEGINNER
        if score_val >= 80.0:
            proficiency = ProficiencyLevel.EXPERT
        elif score_val >= 55.0:
            proficiency = ProficiencyLevel.ADVANCED
        elif score_val >= 30.0:
            proficiency = ProficiencyLevel.INTERMEDIATE

        return {
            "category": "Leadership",
            "confidence_score": round(score_val, 2),
            "experience_score": round(score_val, 2),
            "depth_score": round(score_val, 2),
            "breadth_score": round(score_val, 2),
            "proficiency": proficiency,
            "explanation": {
                "summary": f"Leadership score assessed as {round(score_val, 1)}%.",
                "details": [
                    f"Identified {resume_indicators} leadership markers in candidate work experience descriptions.",
                    f"GitHub follower counts indicate peer verification coefficient: {followers} followers."
                ],
                "factors": {"followers": followers, "resume_indicators": resume_indicators}
            }
        }
