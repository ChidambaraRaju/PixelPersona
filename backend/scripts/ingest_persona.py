#!/usr/bin/env python3
"""CLI script to ingest a persona into Chroma using langchain_chroma."""
import argparse
import json
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_core.documents import Document

from pixelpersona.scraping.wikipedia import WikipediaScraper
from pixelpersona.scraping.wikiquote import WikiquoteScraper
from pixelpersona.scraping.gutenberg import GutenbergScraper
from pixelpersona.processing.chunker import PersonaChunker
from pixelpersona.processing.embedder import LocalEmbedder
from pixelpersona.processing.validator import DataValidator
from pixelpersona.storage.chroma_client import ChromaCollectionManager
from pixelpersona.config import RAW_DATA_DIR

def save_raw_content(persona_name: str, source_name: str, result: dict):
    """Save raw scraped content to data/raw/{persona}/{source}.json"""
    raw_dir = RAW_DATA_DIR / persona_name.replace(" ", "_")
    raw_dir.mkdir(parents=True, exist_ok=True)

    output_file = raw_dir / f"{source_name}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "persona": persona_name,
            "source": source_name,
            "url": result.get("url", ""),
            "title": result.get("title", result.get("sections", {}).keys() if result.get("sections") else []),
            "content": result.get("content", ""),
            "sections": result.get("sections", {})
        }, f, indent=2, ensure_ascii=False)

    return output_file

def ingest_persona(persona_name: str):
    """Ingest a persona from all sources into Chroma and save raw data."""
    print(f"Starting ingestion for: {persona_name}")

    # Initialize components
    scrapers = {
        "wikipedia": WikipediaScraper(),
        "wikiquote": WikiquoteScraper(),
        "gutenberg": GutenbergScraper()
    }
    chunker = PersonaChunker()
    embedder = LocalEmbedder()
    validator = DataValidator()
    collection_manager = ChromaCollectionManager(embedding_function=embedder)

    all_documents = []
    raw_files_saved = []

    # Create raw data directory for this persona
    raw_persona_dir = RAW_DATA_DIR / persona_name.replace(" ", "_")
    raw_persona_dir.mkdir(parents=True, exist_ok=True)

    # Scrape from each source
    for source_name, scraper in scrapers.items():
        print(f"Scraping from {source_name}...")
        try:
            result = scraper.scrape(persona_name)
            if result and result.get("content"):
                # Minimal validation
                if not validator.validate_content(result["content"]):
                    print(f"  {source_name}: Content validation failed, skipping")
                    continue

                # Save raw content
                raw_file = save_raw_content(persona_name, source_name, result)
                raw_files_saved.append(str(raw_file))
                print(f"  {source_name}: Raw content saved to {raw_file}")

                # Create LangChain Document and chunk
                doc = Document(
                    page_content=result["content"],
                    metadata={
                        "source_type": source_name,
                        "source_url": result.get("url", ""),
                        "section": result.get("title", f"{source_name} section"),
                        "persona": persona_name
                    }
                )

                # Chunk the document with persona metadata
                chunks = chunker.chunk_documents(
                    [doc],
                    metadata_updates={"persona": persona_name}
                )

                all_documents.extend(chunks)
                print(f"  {source_name}: {len(chunks)} chunks created")
        except Exception as e:
            print(f"  {source_name}: Error - {e}")

    if not all_documents:
        print("No content scraped. Ingestion failed.")
        return

    # Store in Chroma (langchain_chroma handles embedding internally)
    print(f"Embedding and storing {len(all_documents)} chunks in Chroma...")
    collection_manager.add_documents(persona_name, all_documents)

    print(f"\nIngestion complete for {persona_name}!")
    print(f"Raw data saved to: {raw_persona_dir}")
    print(f"Files saved: {len(raw_files_saved)}")
    print(f"Chunks stored in Chroma: {len(all_documents)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a persona into Chroma")
    parser.add_argument("persona_name", help="Name of the persona to ingest")
    args = parser.parse_args()
    ingest_persona(args.persona_name)