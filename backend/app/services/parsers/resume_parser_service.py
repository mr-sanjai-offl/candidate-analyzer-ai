"""Orchestrates parsing of resumes based on MIME type."""

import logging
from typing import Optional

from app.core.exceptions import BadRequestException
from app.services.parsers.docx_parser import DOCXParser
from app.services.parsers.extraction_service import ExtractionService
from app.services.parsers.ocr_service import OCRService
from app.services.parsers.pdf_parser import PDFParser

logger = logging.getLogger(__name__)

class ResumeParserService:
    """Service to parse, OCR, and extract data from a resume file."""

    def __init__(self):
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.ocr_service = OCRService()
        self.extraction_service = ExtractionService()

    def parse_and_extract(self, file_bytes: bytes, mime_type: str) -> tuple[str, dict]:
        """Parse text, optionally run OCR, and extract JSON data."""
        raw_text = ""
        
        # 1. Parse based on MIME
        if mime_type == "application/pdf":
            raw_text = self.pdf_parser.parse(file_bytes)
        elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            raw_text = self.docx_parser.parse(file_bytes)
        elif mime_type == "text/plain":
            try:
                raw_text = file_bytes.decode('utf-8')
            except UnicodeDecodeError:
                raw_text = file_bytes.decode('latin-1', errors='ignore')
        elif mime_type in ["image/png", "image/jpeg", "image/jpg"]:
            # For images, bypass normal parsing and go straight to OCR
            raw_text = ""
        else:
            raise BadRequestException(f"Unsupported MIME type for parsing: {mime_type}")
            
        # 2. OCR Fallback (if text is empty or too short, it might be scanned)
        if len(raw_text.strip()) < 50 and mime_type in ["application/pdf", "image/png", "image/jpeg", "image/jpg"]:
            logger.info(f"Text too short ({len(raw_text.strip())} chars), attempting OCR...")
            ocr_text = self.ocr_service.extract_text(file_bytes, mime_type)
            if ocr_text:
                raw_text = ocr_text
                
        # 3. Extraction
        if not raw_text.strip():
            logger.warning("No text could be extracted from the document.")
            structured_data = {}
        else:
            structured_data = self.extraction_service.extract_structured_data(raw_text)
            
        return raw_text, structured_data
