"""Pytest fixtures for PixelPersona backend tests."""
import pytest
from pathlib import Path
import tempfile
import shutil

@pytest.fixture
def temp_data_dir():
    """Temporary directory for test data."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # On Windows, Chroma's sqlite may keep files open - ignore cleanup errors
    try:
        shutil.rmtree(temp_dir)
    except (PermissionError, OSError):
        pass  # Ignore cleanup errors on Windows

@pytest.fixture
def sample_persona_data():
    """Sample scraped persona data for testing."""
    return {
        "name": "Albert Einstein",
        "sources": [
            {
                "source_type": "wikipedia",
                "url": "https://en.wikipedia.org/wiki/Albert_Einstein",
                "content": "Albert Einstein was a German-born theoretical physicist...",
                "section": "Biography"
            },
            {
                "source_type": "wikiquote",
                "url": "https://en.wikiquote.org/wiki/Albert_Einstein",
                "content": "Imagination is more important than knowledge...",
                "section": "Quotes"
            }
        ]
    }