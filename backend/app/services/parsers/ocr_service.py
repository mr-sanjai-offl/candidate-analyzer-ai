"""OCR Service using Tesseract."""

import logging
import io

import fitz  # PyMuPDF
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)

class OCRService:
    """Extracts text from images and scanned PDFs using Tesseract OCR."""

    def extract_text(self, file_bytes: bytes, mime_type: str) -> str:
        """Extract text using OCR."""
        text_content = []
        try:
            if mime_type == "application/pdf":
                # Convert PDF pages to images and run OCR
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x resolution
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    text = pytesseract.image_to_string(img)
                    text_content.append(text)
                doc.close()
            elif mime_type in ["image/png", "image/jpeg", "image/jpg"]:
                img = Image.open(io.BytesIO(file_bytes))
                text = pytesseract.image_to_string(img)
                text_content.append(text)
            else:
                logger.warning(f"Unsupported MIME type for OCR: {mime_type}")
        except Exception as e:
            logger.error(f"Error during OCR extraction: {e}")
            
        return "\n".join(text_content)
