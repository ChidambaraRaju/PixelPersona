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
    validator.validate(data, required_fields=["name", "content"])  # no exception = pass

def test_validate_required_fields_fail():
    validator = DataValidator()
    data = {"name": "Albert Einstein"}
    with pytest.raises(ValidationError, match="Missing or empty required field: content"):
        validator.validate(data, required_fields=["name", "content"])

def test_validate_required_fields_empty_string():
    validator = DataValidator()
    data = {"name": "", "content": "Some content"}
    with pytest.raises(ValidationError, match="Missing or empty required field: name"):
        validator.validate(data, required_fields=["name", "content"])

def test_validate_content_not_corrupt():
    validator = DataValidator()
    validator.validate_content("Normal text content that has enough words to pass validation")

def test_validate_content_corrupt_non_printable():
    validator = DataValidator()
    corrupt = "\x00\x01\x02" * 100
    with pytest.raises(ValidationError, match="more than 50% non-printable"):
        validator.validate_content(corrupt)

def test_validate_content_too_short():
    validator = DataValidator()
    with pytest.raises(ValidationError, match="fewer than 10 words"):
        validator.validate_content("Hi")

def test_validate_content_whitespace_only():
    validator = DataValidator()
    with pytest.raises(ValidationError, match="too short, empty, or whitespace only"):
        validator.validate_content("   \n\t   ")

def test_validate_content_exactly_ten_words():
    validator = DataValidator()
    ten_words = "one two three four five six seven eight nine ten"
    validator.validate_content(ten_words)  # exactly 10 words should pass
