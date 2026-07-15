"""Extraction Service.

Maps parsed text into structured JSON.
"""

import logging
import re

from app.services.parsers.normalization_service import NormalizationService

logger = logging.getLogger(__name__)

class ExtractionService:
    """Extracts structured data from raw text."""

    def extract_structured_data(self, text: str) -> dict:
        """Extract sections and entities from text."""
        # This is a naive heuristic-based extraction for demonstration.
        # In a real-world scenario, this would use NLP (e.g. spaCy) or an LLM API.
        
        data = {
            "personal_information": {},
            "education": [],
            "experience": [],
            "skills": [],
            "projects": [],
            "certifications": [],
            "languages": [],
            "social_links": [],
            "metadata": {"extracted_sections": []}
        }
        
        # Simple Email Extraction
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            data["personal_information"]["email"] = {
                "value": NormalizationService.normalize_email(email_match.group(0)),
                "confidence": 0.95,
                "source": "regex"
            }

        # Simple Phone Extraction
        phone_match = re.search(r'(\+\d{1,2}\s?)?1?\-?\.?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', text)
        if phone_match:
            data["personal_information"]["phone"] = {
                "value": NormalizationService.normalize_phone(phone_match.group(0)),
                "confidence": 0.90,
                "source": "regex"
            }

        # Skills Heuristic
        skills_keywords = ["python", "java", "c++", "react", "fastapi", "docker", "sql"]
        found_skills = []
        for skill in skills_keywords:
            if re.search(rf'\b{skill}\b', text, re.IGNORECASE):
                found_skills.append({
                    "value": skill.capitalize(),
                    "confidence": 0.85,
                    "source": "keyword_match"
                })
        data["skills"] = found_skills

        return data
