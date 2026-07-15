"""PDF Parser using PyMuPDF and pdfplumber."""

import logging
import io

import fitz  # PyMuPDF
import pdfplumber

from app.services.parsers.base import BaseParser

logger = logging.getLogger(__name__)

class PDFParser(BaseParser):
    """Extracts text from PDF files."""

    def parse(self, file_bytes: bytes) -> str:
        """Extract text using PyMuPDF, fallback to pdfplumber if needed."""
        text_content = []
        try:
            # Load with PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                text = page.get_text()
                if text.strip():
                    text_content.append(text)
            doc.close()
            
            if not text_content:
                # If no text was extracted (might be scanned or malformed), try pdfplumber
                logger.info("PyMuPDF returned empty text. Trying pdfplumber...")
                with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text_content.append(extracted)
                            
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            
        return "\n".join(text_content)
