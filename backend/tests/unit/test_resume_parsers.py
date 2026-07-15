"""Unit tests for ResumeParserService and sub-parsers."""

import pytest
from unittest.mock import MagicMock, patch

from app.services.parsers.normalization_service import NormalizationService
from app.services.parsers.extraction_service import ExtractionService
from app.services.parsers.resume_parser_service import ResumeParserService


# ── NormalizationService ──────────────────────────────────────────────────────

class TestNormalizationService:
    def test_normalize_phone_strips_dashes(self):
        result = NormalizationService.normalize_phone("+1-800-555-1234")
        assert result == "+18005551234"

    def test_normalize_phone_strips_parens(self):
        result = NormalizationService.normalize_phone("(800) 555-1234")
        assert result == "8005551234"

    def test_normalize_email_lowercases(self):
        result = NormalizationService.normalize_email("John.Doe@Example.COM")
        assert result == "john.doe@example.com"

    def test_normalize_email_strips_whitespace(self):
        result = NormalizationService.normalize_email("  john@example.com  ")
        assert result == "john@example.com"

    def test_deduplicate_preserves_order(self):
        result = NormalizationService.deduplicate(["Python", "Java", "Python", "Go"])
        assert result == ["Python", "Java", "Go"]

    def test_deduplicate_case_insensitive(self):
        result = NormalizationService.deduplicate(["python", "Python", "PYTHON"])
        assert len(result) == 1

    def test_deduplicate_strips_whitespace(self):
        result = NormalizationService.deduplicate(["  Python  ", "Python"])
        assert len(result) == 1


# ── ExtractionService ─────────────────────────────────────────────────────────

class TestExtractionService:
    def setup_method(self):
        self.service = ExtractionService()

    def test_extracts_email(self):
        text = "Contact me at john.doe@example.com for more info."
        result = self.service.extract_structured_data(text)
        assert "email" in result["personal_information"]
        assert result["personal_information"]["email"]["value"] == "john.doe@example.com"

    def test_extracts_phone(self):
        text = "Phone: +1-800-555-1234"
        result = self.service.extract_structured_data(text)
        assert "phone" in result["personal_information"]

    def test_extracts_skills(self):
        text = "Proficient in Python, FastAPI, Docker and SQL."
        result = self.service.extract_structured_data(text)
        skill_values = [s["value"].lower() for s in result["skills"]]
        assert "python" in skill_values
        assert "docker" in skill_values
        assert "sql" in skill_values

    def test_returns_confidence_and_source(self):
        text = "Email: test@example.com"
        result = self.service.extract_structured_data(text)
        email_field = result["personal_information"].get("email")
        assert email_field is not None
        assert "confidence" in email_field
        assert "source" in email_field
        assert 0 <= email_field["confidence"] <= 1.0

    def test_empty_text_returns_empty_sections(self):
        result = self.service.extract_structured_data("")
        assert isinstance(result["skills"], list)
        assert isinstance(result["education"], list)

    def test_schema_has_required_keys(self):
        result = self.service.extract_structured_data("hello")
        required_keys = {
            "personal_information",
            "education",
            "experience",
            "skills",
            "projects",
            "certifications",
            "languages",
            "social_links",
            "metadata",
        }
        assert required_keys.issubset(result.keys())


# ── ResumeParserService ───────────────────────────────────────────────────────

class TestResumeParserService:
    def setup_method(self):
        self.service = ResumeParserService()

    def test_parses_plain_text(self):
        text = b"John Doe\nSoftware Engineer\nPython, FastAPI"
        raw_text, structured = self.service.parse_and_extract(text, "text/plain")
        assert "John Doe" in raw_text
        assert isinstance(structured, dict)

    def test_triggers_ocr_when_pdf_returns_empty_text(self):
        """If PDF parser returns no text, OCRService should be invoked."""
        with (
            patch.object(self.service.pdf_parser, "parse", return_value=""),
            patch.object(
                self.service.ocr_service, "extract_text", return_value="OCR extracted text"
            ) as mock_ocr,
        ):
            raw_text, _ = self.service.parse_and_extract(b"%PDF-1.4", "application/pdf")
            mock_ocr.assert_called_once()
            assert "OCR extracted text" in raw_text

    def test_does_not_trigger_ocr_when_pdf_has_text(self):
        """If PDF parser returns sufficient text, OCR must NOT be called."""
        long_text = "A" * 200
        with (
            patch.object(self.service.pdf_parser, "parse", return_value=long_text),
            patch.object(self.service.ocr_service, "extract_text") as mock_ocr,
        ):
            raw_text, _ = self.service.parse_and_extract(b"%PDF-1.4", "application/pdf")
            mock_ocr.assert_not_called()

    def test_unsupported_mime_raises(self):
        from app.core.exceptions import BadRequestException
        with pytest.raises(BadRequestException):
            self.service.parse_and_extract(b"data", "application/x-excel")
