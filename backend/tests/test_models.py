"""Tests for persona data models."""
import pytest
from pixelpersona.models.persona import Persona, PersonaChunk, SourceType

def test_persona_creation():
    persona = Persona(name="Albert Einstein", description="German physicist")
    assert persona.name == "Albert Einstein"
    assert persona.description == "German physicist"

def test_persona_chunk_creation():
    chunk = PersonaChunk(
        content="Sample content about Einstein's life...",
        source_type=SourceType.WIKIPEDIA,
        source_url="https://en.wikipedia.org/wiki/Albert_Einstein",
        section="Biography",
        persona="Albert Einstein"
    )
    assert chunk.content == "Sample content about Einstein's life..."
    assert chunk.source_type == SourceType.WIKIPEDIA

def test_source_type_enum():
    assert SourceType.WIKIPEDIA.value == "wikipedia"
    assert SourceType.WIKISUCCESS.value == "wikiquote"
    assert SourceType.GUTENBERG.value == "gutenberg"
    assert SourceType.ARCHIVE.value == "archive"

def test_available_personas():
    from pixelpersona.models.persona import AVAILABLE_PERSONAS, get_persona_description, list_personas

    # Check all V1 personas exist
    assert "Albert Einstein" in AVAILABLE_PERSONAS
    assert "Nikola Tesla" in AVAILABLE_PERSONAS
    assert "APJ Abdul Kalam" in AVAILABLE_PERSONAS
    assert "Mahatma Gandhi" in AVAILABLE_PERSONAS

    # Check get_persona_description
    desc = get_persona_description("Albert Einstein")
    assert desc is not None
    assert "physicist" in desc.lower()

    # Check unknown persona returns None
    assert get_persona_description("Unknown Person") is None

    # Check list_personas returns dict
    personas = list_personas()
    assert isinstance(personas, dict)
    assert len(personas) == 4