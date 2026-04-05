"""Minimal data validation for scraped content."""
import re
from typing import Dict, Any, List

class ValidationError(Exception):
    """Raised when validation fails."""
    pass

class DataValidator:
    """Minimal validator for scraped persona data."""

    def validate(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """Check if all required fields are present and non-empty.

        Raises:
            ValidationError: if any required field is missing or empty.
        """
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(f"Missing or empty required field: {field}")

    def validate_content(self, content: str) -> None:
        """Check if content is not corrupt.

        Content is considered corrupt if:
        - More than 50% non-printable characters
        - Less than 10 words

        Raises:
            ValidationError: if content fails validation.
        """
        if not content or not content.strip():
            raise ValidationError("Content too short, empty, or whitespace only")

        # Check for excessive non-printable characters
        printable = sum(1 for c in content if c.isprintable() or c in '\n\t')
        if printable / len(content) < 0.5:
            raise ValidationError("Content contains more than 50% non-printable characters")

        # Check minimum word count
        word_count = len(content.split())
        if word_count < 10:
            raise ValidationError(f"Content has fewer than 10 words ({word_count} found)")