"""Tests for data validator."""
import pytest
from pixelpersona.processing.validator import DataValidator, ValidationError

def test_validate_required_fields_pass():
    validator = DataValidator()
    data = {
        "name": "Albert Einstein",
        "content": "Some content",
        "source_type": "wikipedia"
    }
    result = validator.validate(data, required_fields=["name", "content"])
    assert result is True

def test_validate_required_fields_fail():
    validator = DataValidator()
    data = {"name": "Albert Einstein"}
    result = validator.validate(data, required_fields=["name", "content"])
    assert result is False

def test_validate_required_fields_empty_string():
    validator = DataValidator()
    data = {"name": "", "content": "Some content"}
    result = validator.validate(data, required_fields=["name", "content"])
    assert result is False

def test_validate_content_not_corrupt():
    validator = DataValidator()
    # Valid content (10+ words)
    assert validator.validate_content("Normal text content that has enough words to pass validation") is True
    # Corrupt: mostly non-printable characters
    corrupt = "\x00\x01\x02" * 100
    assert validator.validate_content(corrupt) is False

def test_validate_content_too_short():
    validator = DataValidator()
    # Too few words
    assert validator.validate_content("Hi") is False
    # Exactly 10 words should pass
    ten_words = "one two three four five six seven eight nine ten"
    assert validator.validate_content(ten_words) is True

def test_validate_content_whitespace_only():
    validator = DataValidator()
    assert validator.validate_content("   \n\t   ") is False