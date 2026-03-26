#!/usr/bin/env python3
"""CLI script to ingest a persona into Chroma using langchain_chroma."""
import argparse
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

def ingest_persona(persona_name: str):
    """Ingest a persona from all sources into Chroma."""
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

    print(f"Ingestion complete for {persona_name}!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a persona into Chroma")
    parser.add_argument("persona_name", help="Name of the persona to ingest")
    args = parser.parse_args()
    ingest_persona(args.persona_name)