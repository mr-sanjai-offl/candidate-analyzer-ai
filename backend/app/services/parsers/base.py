"""Base parser for resume text extraction."""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseParser(ABC):
    """Abstract base class for all file parsers."""
    
    @abstractmethod
    def parse(self, file_bytes: bytes) -> str:
        """Extract text from raw file bytes.
        
        Args:
            file_bytes: Raw bytes of the file.
            
        Returns:
            Extracted text as a string.
        """
        pass
