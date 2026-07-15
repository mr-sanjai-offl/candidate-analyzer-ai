"""Unit tests for the capability evaluation engines.

Tests deterministic skill extraction, alias normalization, capability scoring,
readiness evaluations, and gap analyses.
"""

import pytest

from app.database.models.enums import SkillCategory, ProficiencyLevel
from app.scoring.skill_engine import SkillExtractionEngine
from app.scoring.scoring_engine import CapabilityScoringEngine
from app.scoring.readiness_engine import ReadinessAssessmentEngine
from app.scoring.gap_analysis_engine import GapAnalysisEngine


# ── Normalization & Extraction Tests ──────────────────────────────────────────

class TestSkillExtraction:
    def test_alias_normalization(self):
        engine = SkillExtractionEngine()
        assert engine.normalize_name("FastAPI") == "Python Backend"
        assert engine.normalize_name("Flask") == "Python Backend"
        assert engine.normalize_name("Django") == "Python Backend"
        assert engine.normalize_name("C++") == "C++"
        assert engine.normalize_name("cpp") == "C++"
        assert engine.normalize_name("JS") == "Node.js"
        assert engine.normalize_name("javascript") == "Node.js"
        assert engine.normalize_name("nodejs") == "Node.js"
        assert engine.normalize_name("Docker Compose") == "Docker"
        assert engine.normalize_name("docker") == "Docker"

    def test_resolve_categories(self):
        engine = SkillExtractionEngine()
        assert engine.resolve_category("Python") == SkillCategory.LANGUAGE
        assert engine.resolve_category("Python Backend") == SkillCategory.FRAMEWORK
        assert engine.resolve_category("Docker") == SkillCategory.TOOL
        assert engine.resolve_category("PostgreSQL") == SkillCategory.DATABASE

    def test_deterministic_extraction_sources(self):
        engine = SkillExtractionEngine()
        resume = {"skills": ["Python", "FastAPI"], "work_experience": [{"description": "Developed features in AWS and Docker"}]}
        github = {
            "primary_language": "TypeScript",
            "skills": [{"name": "TypeScript", "relevance_score": 0.9}],
            "projects": [{"name": "repo1", "primary_language": "TypeScript", "languages": ["TypeScript", "CSS"]}],
        }
        leetcode = {"problems_solved": 50, "topic_distribution": {"Dynamic Programming": 10}}
        codeforces = {"rating": 1400, "topic_distribution": {"Greedy": 5}}

        res = engine.extract_skills(
            resume_data=resume,
            github_profile=github,
            leetcode_profile=leetcode,
            codeforces_profile=codeforces,
        )

        assert "Python" in res
        assert "Python Backend" in res  # normalized from FastAPI
        assert "TypeScript" in res
        assert "Dynamic Programming" in res
        assert "Greedy" in res
        assert "Docker" in res  # from work experience text scan

        # Check evidence links
        assert len(res["Python"]["evidences"]) >= 1
        assert res["Python"]["evidences"][0]["source"] == "RESUME"


# ── Scoring Engine Tests ──────────────────────────────────────────────────────

class TestScoringEngine:
    def test_scoring_formulas_with_evidence(self):
        engine = CapabilityScoringEngine()
        skills = {
            "Python": {
                "name": "Python",
                "category": SkillCategory.LANGUAGE,
                "evidences": [
                    {"source": "RESUME", "weight": 0.3, "confidence": 70, "evidence": "Resume match", "verification_state": "CLAIMED"},
                    {"source": "GITHUB", "weight": 0.8, "confidence": 95, "evidence": "Primary lang", "verification_state": "VERIFIED"},
                ]
            }
        }

        scores = engine.compute_category_scores(skills)
        lang_score = scores.get("Programming Languages", {})
        
        assert lang_score["category"] == "Programming Languages"
        assert lang_score["confidence_score"] > 0
        assert lang_score["experience_score"] > 0
        assert lang_score["depth_score"] > 0
        assert lang_score["breadth_score"] == 20.0  # 1 skill * 20.0
        assert lang_score["proficiency"] in (ProficiencyLevel.INTERMEDIATE, ProficiencyLevel.ADVANCED, ProficiencyLevel.EXPERT)
        assert "summary" in lang_score["explanation"]


# ── Readiness & Gap Analysis Tests ───────────────────────────────────────────

class TestReadinessAndGaps:
    def test_readiness_calculation(self):
        engine = ReadinessAssessmentEngine()
        category_scores = {
            "Programming Languages": {"experience_score": 80.0},
            "Frameworks": {"experience_score": 75.0},
        }
        extracted_skills = {"python": {}, "react": {}}

        res = engine.assess_readiness(category_scores, extracted_skills)
        backend = res.get("Backend", {})
        assert backend["score"] > 0.0
        assert "missing_skills" in backend["explanation"]

    def test_gap_analysis(self):
        engine = GapAnalysisEngine()
        category_scores = {"Programming Languages": {"experience_score": 50.0}}
        extracted_skills = {
            "Python": {"evidences": [{"weight": 0.8}]},
            "FastAPI": {"evidences": [{"weight": 0.3}]},
        }
        readiness_reports = {"Backend": {"score": 60.0}}

        res = engine.compute_gap_analysis(category_scores, extracted_skills, readiness_reports)
        assert res["target_role"] == "Backend"
        assert "Python" in res["strong_skills"]
        assert "FastAPI" in res["weak_skills"]
        assert len(res["recommended_projects"]) >= 1
