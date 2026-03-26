"""Minimal data validation for scraped content."""
import re
from typing import Dict, Any, List

class ValidationError(Exception):
    """Raised when validation fails."""
    pass

class DataValidator:
    """Minimal validator for scraped persona data."""

    def validate(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Check if all required fields are present and non-empty."""
        for field in required_fields:
            if field not in data or not data[field]:
                return False
        return True

    def validate_content(self, content: str) -> bool:
        """Check if content is not corrupt.

        Content is considered corrupt if:
        - More than 50% non-printable characters
        - Less than 10 words
        """
        if not content or len(content.strip()) < 10:
            return False

        # Check for excessive non-printable characters
        printable = sum(1 for c in content if c.isprintable() or c in '\n\t')
        if printable / len(content) < 0.5:
            return False

        # Check minimum word count
        word_count = len(content.split())
        if word_count < 10:
            return False

        return True