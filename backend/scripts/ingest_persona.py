#!/usr/bin/env python3
"""CLI script to ingest a persona into Chroma from local raw data files.

Reads all files from data/raw/{persona}/ and ingests them into Chroma.
Supports JSON files (scraped Wikipedia/Wikiquote) and plain text files (manual downloads).
"""
import argparse
import json
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_core.documents import Document

from pixelpersona.processing.chunker import PersonaChunker
from pixelpersona.processing.embedder import LocalEmbedder
from pixelpersona.processing.validator import DataValidator
from pixelpersona.storage.chroma_client import ChromaCollectionManager
from pixelpersona.config import RAW_DATA_DIR


def load_raw_files(persona_dir: Path) -> list[tuple[str, dict]]:
    """Load all raw data files from persona directory.

    Returns list of (filename, data) tuples for JSON files,
    and (filename, data) for text files with content in 'content' field.
    """
    files_data = []

    if not persona_dir.exists():
        return files_data

    for file_path in persona_dir.iterdir():
        if file_path.suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                files_data.append((file_path.stem, data))
        elif file_path.suffix == ".txt":
            # Plain text file (manual download from Gutenberg/Archive.org)
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                # Remove UTF-8 BOM if present
                if content and ord(content[0]) == 0xFEFF:
                    content = content[1:]
                data = {
                    "persona": persona_dir.name.replace("_", " "),
                    "source": "primary_source",
                    "title": file_path.stem,
                    "content": content
                }
                files_data.append((file_path.stem, data))

    return files_data


def ingest_persona(persona_name: str):
    """Ingest a persona from raw data files into Chroma."""
    print(f"Starting ingestion for: {persona_name}")

    # Initialize components
    chunker = PersonaChunker()
    embedder = LocalEmbedder()
    validator = DataValidator()
    collection_manager = ChromaCollectionManager(embedding_function=embedder)

    # Load raw data directory
    persona_dir = RAW_DATA_DIR / persona_name.replace(" ", "_")

    # Load all raw files
    raw_files = load_raw_files(persona_dir)

    if not raw_files:
        print(f"No raw data found in {persona_dir}")
        return

    print(f"Found {len(raw_files)} raw data files:")
    for filename, data in raw_files:
        print(f"  - {filename}: {len(data.get('content', ''))} chars")

    all_documents = []

    # Process each file
    for source_name, data in raw_files:
        content = data.get("content", "")

        if not content:
            print(f"  {source_name}: No content, skipping")
            continue

        # Validate content
        if not validator.validate_content(content):
            print(f"  {source_name}: Content validation failed, skipping")
            continue

        # Create LangChain Document
        doc = Document(
            page_content=content,
            metadata={
                "source_type": data.get("source", "unknown"),
                "source_url": data.get("url", ""),
                "title": data.get("title", source_name),
                "persona": persona_name
            }
        )

        # Chunk the document
        chunks = chunker.chunk_documents(
            [doc],
            metadata_updates={"persona": persona_name}
        )

        all_documents.extend(chunks)
        print(f"  {source_name}: {len(chunks)} chunks created")

    if not all_documents:
        print("No content to ingest. Ingestion failed.")
        return

    # Store in Chroma
    print(f"\nEmbedding and storing {len(all_documents)} chunks in Chroma...")
    collection_manager.add_documents(persona_name, all_documents)

    print(f"\nIngestion complete for {persona_name}!")
    print(f"Total chunks stored in Chroma: {len(all_documents)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a persona into Chroma from raw data files")
    parser.add_argument("persona_name", help="Name of the persona to ingest")
    args = parser.parse_args()
    ingest_persona(args.persona_name)