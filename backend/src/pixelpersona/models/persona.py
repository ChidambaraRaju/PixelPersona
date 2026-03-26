"""Persona data models and available personas registry."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict

class SourceType(Enum):
    """Source types for persona data."""
    WIKIPEDIA = "wikipedia"
    WIKISUCCESS = "wikiquote"
    GUTENBERG = "gutenberg"
    ARCHIVE = "archive"

@dataclass
class Persona:
    """Represents a persona."""
    name: str
    description: str

@dataclass
class PersonaChunk:
    """Represents a chunk of persona data."""
    content: str
    source_type: SourceType
    source_url: str
    section: str
    persona: str
    metadata: Optional[dict] = None

# V1 Available Personas - single source of truth for all backend components
AVAILABLE_PERSONAS: Dict[str, str] = {
    "Albert Einstein": "German-born theoretical physicist and philosopher of science",
    "Nikola Tesla": "Inventor and electrical engineer known for AC power systems",
    "APJ Abdul Kalam": "Aerospace scientist and 11th President of India",
    "Mahatma Gandhi": "Leader of Indian independence movement and philosopher"
}

def get_persona_description(persona_name: str) -> Optional[str]:
    """Get description for a persona by name. Returns None if persona not found."""
    return AVAILABLE_PERSONAS.get(persona_name)

def list_personas() -> Dict[str, str]:
    """Return all available personas."""
    return AVAILABLE_PERSONAS.copy()