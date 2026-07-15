"""DOCX Parser using python-docx."""

import logging
import io

import docx

from app.services.parsers.base import BaseParser

logger = logging.getLogger(__name__)

class DOCXParser(BaseParser):
    """Extracts text from DOCX files."""

    def parse(self, file_bytes: bytes) -> str:
        """Extract text using python-docx."""
        text_content = []
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            
        return "\n".join(text_content)
