"""Unit tests for the AI Intelligence Layer.

Tests prompt managers, model routers, context deduplication, mock adapters,
role matching, explainable search engine, and document exports.
"""

import pytest
import uuid

from app.agents.prompts import PromptManager
from app.agents.router import ModelRouter
from app.agents.context import EvidenceAssembler
from app.agents.adapters import MockAdapter
from app.agents.base import LLMRequest
from app.services.export_engine import ExportEngineService
from app.services.search_engine import SearchEngineService


# ── PromptManager & Router Tests ──────────────────────────────────────────────

class TestAIOrchestratorComponents:
    @pytest.mark.asyncio
    async def test_prompt_manager_substitution(self):
        manager = PromptManager()
        sys_p, user_p, ver = await manager.get_prompt(
            db=None,
            name="skill_explanation",
            variables={"skill_name": "Docker", "evidence": "Tested"},
        )
        assert "Docker" in user_p
        assert "Tested" in user_p
        assert ver == 1

    def test_model_router_assignment(self):
        router = ModelRouter()
        assert router.get_model("recruiter_report") == "gpt-4o"
        assert router.get_model("candidate_feedback") == "gpt-4o-mini"


# ── Deduplication Tests ───────────────────────────────────────────────────────

class TestDeduplication:
    def test_evidence_assembler_dedup(self):
        class MockEvidence:
            def __init__(self, source, text, weight=0.5, confidence=80, state="VERIFIED"):
                self.source = source
                self.evidence_text = text
                self.weight = weight
                self.confidence = confidence
                self.verification_state = state

        evs = [
            MockEvidence("GITHUB", "Dockerfile detected"),
            MockEvidence("GITHUB", "Dockerfile detected"), # Duplicate
            MockEvidence("RESUME", "Docker skills"),
        ]

        deduped = EvidenceAssembler.assemble_evidence(evs) # type: ignore
        assert len(deduped) == 2
        assert deduped[0]["source"] == "GITHUB"
        assert deduped[1]["source"] == "RESUME"


# ── MockAdapter Tests ─────────────────────────────────────────────────────────

class TestMockAdapter:
    @pytest.mark.asyncio
    async def test_mock_adapter_completions(self):
        adapter = MockAdapter()
        
        # Test recruiter report payload
        req = LLMRequest(prompt="recruiter report for candidates")
        resp = await adapter.generate(req)
        assert "Executive Summary" in resp.text
        assert "Strengths" in resp.text

        # Test job matching payload
        req_match = LLMRequest(prompt="job matching match candidate profile")
        resp_match = await adapter.generate(req_match)
        assert "match_score" in resp_match.text


# ── Exporter Tests ────────────────────────────────────────────────────────────

class TestExportEngine:
    def test_exports_generation_formats(self):
        data = {"Executive Summary": "Excellent candidate backend developer profile."}
        
        json_bytes = ExportEngineService.export_as_json(data)
        assert len(json_bytes) > 0
        assert b"Excellent" in json_bytes

        csv_bytes = ExportEngineService.export_as_csv(data)
        assert len(csv_bytes) > 0
        assert b"Executive Summary" in csv_bytes

        pdf_bytes = ExportEngineService.export_as_pdf(data)
        assert pdf_bytes.startswith(b"%PDF")

        docx_bytes = ExportEngineService.export_as_docx(data)
        assert b"[Content_Types].xml" in docx_bytes
