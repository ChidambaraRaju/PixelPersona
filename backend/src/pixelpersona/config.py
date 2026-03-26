"""Environment configuration for PixelPersona backend."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CHROMA_DIR = PROJECT_ROOT / "chroma_data"

# Chroma
CHROMA_PERSIST_DIR = str(CHROMA_DIR)

# Embedding
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_BATCH_SIZE = 100

# Chunking (character-based for RecursiveCharacterTextSplitter)
# ~400-800 words ≈ ~2000-4000 chars; using 3000 as middle ground
CHUNK_SIZE = 3000
CHUNK_OVERLAP = 300

# Retrieval
TOP_K_CHUNKS = 5

# LLM - GroqCloud
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GPT_OSS_MODEL = "GroqCloud/GPT-OSS-20B"
REPHRASER_MODEL = "GroqCloud/llama-3.1-8b-instant"

# Rephraser
REPHRASER_SYSTEM_PROMPT = """Rephrase the following user query to improve semantic search retrieval.
Keep it concise (1-2 sentences). Return only the rephrased query."""

# Persona agent prompt template
PERSONA_AGENT_PROMPT_TEMPLATE = """You are {persona_name}, {persona_description}.

Your response must:
1. Be grounded in the provided context
2. Match {persona_name}'s tone, style, and knowledge
3. Never fabricate facts outside the provided context

Context:
{context}

Remember: If the context doesn't contain enough information to answer, say so."""