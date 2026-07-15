"""Gap Analysis Engine.

Determines strong, weak, and missing skills, prioritizes learning paths, and
suggests recommended engineering projects.
"""

from typing import Any

from app.scoring.readiness_engine import ROLE_SKILL_REQUIREMENTS


class GapAnalysisEngine:
    """Computes skill gaps, recommendations, and roadmaps without AI."""

    def __init__(self) -> None:
        self.requirements = ROLE_SKILL_REQUIREMENTS

    def compute_gap_analysis(
        self,
        category_scores: dict[str, dict[str, Any]],
        extracted_skills: dict[str, dict[str, Any]],
        readiness_reports: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate missing skills, weak skills, strong skills, and learning priorities."""
        strong_skills: list[str] = []
        weak_skills: list[str] = []
        missing_skills: set[str] = set()

        # ── 1. Map existing skills strength ──────────────────────────────────
        for name, skill in extracted_skills.items():
            # Get maximum confidence / weight across evidences to estimate score
            evs = skill.get("evidences", [])
            max_weight = max([e["weight"] for e in evs]) if evs else 0.0
            
            if max_weight >= 0.7:
                strong_skills.append(name)
            else:
                weak_skills.append(name)

        # ── 2. Identify missing skills based on the highest readiness role ────
        # Pick the role the candidate scored highest on (representing their target track)
        target_role = "Backend"
        highest_score = -1.0
        for role, report in readiness_reports.items():
            if report.get("score", 0.0) > highest_score:
                highest_score = report.get("score", 0.0)
                target_role = role

        role_reqs = self.requirements.get(target_role, {"skills": []})
        for req_skill in role_reqs["skills"]:
            if req_skill not in [s.lower() for s in extracted_skills.keys()]:
                missing_skills.add(req_skill.title())

        # ── 3. Generate Learning Priority and Recommendations ─────────────────
        learning_priority: list[str] = []
        # Missing skills of target track go first
        learning_priority.extend(list(missing_skills)[:3])
        # Weak skills go next
        learning_priority.extend([w for w in weak_skills if w not in learning_priority][:2])

        recommended_projects = self._generate_recommended_projects(learning_priority, target_role)

        return {
            "target_role": target_role,
            "strong_skills": strong_skills[:10],
            "weak_skills": weak_skills[:10],
            "missing_skills": list(missing_skills)[:10],
            "improvement_areas": [f"Strengthen capability in {s}" for s in weak_skills[:3]],
            "learning_priority": learning_priority[:5],
            "recommended_projects": recommended_projects,
        }

    def _generate_recommended_projects(self, priority_skills: list[str], target_role: str) -> list[dict[str, str]]:
        """Determine specific project templates for candidate improvement."""
        projects = []
        skills_lower = [s.lower() for s in priority_skills]

        if any(s in skills_lower for s in ("python backend", "django", "fastapi", "flask")) or target_role == "Backend":
            projects.append({
                "title": "High-Performance Async API",
                "description": "Build a secure REST/GraphQL API using FastAPI, SQLAlchemy 2.0 (Async), and PostgreSQL. Integrate Redis caching and Celery tasks.",
                "target_skills": "FastAPI, PostgreSQL, Redis, Celery",
            })

        if any(s in skills_lower for s in ("react", "angular", "vue", "javascript", "typescript")) or target_role == "Frontend":
            projects.append({
                "title": "Interactive Client Dashboard",
                "description": "Construct a responsive single-page web app with React, TypeScript, and state management library. Integrate REST api queries.",
                "target_skills": "React, TypeScript, CSS",
            })

        if any(s in skills_lower for s in ("docker", "kubernetes", "devops", "ci/cd")):
            projects.append({
                "title": "Microservices Orchestration Pipeline",
                "description": "Containerize backend and database services using Docker. Author a GitHub Actions workflow to run lint tests, build images, and deploy to Kubernetes.",
                "target_skills": "Docker, Kubernetes, CI/CD",
            })

        # Fallback default project
        if not projects:
            projects.append({
                "title": "End-to-End Enterprise App",
                "description": "Develop a full-featured microservice architecture with API Gateway, JWT auth, PostgreSQL, and Docker container packaging.",
                "target_skills": "Software Architecture, Databases, Containers",
            })

        return projects
