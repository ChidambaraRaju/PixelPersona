#!/usr/bin/env python3
"""Scrape Wikipedia and Wikiquote for a persona, saving raw content to data/raw/{persona}/."""
import argparse
import json
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pixelpersona.scraping.wikipedia import WikipediaScraper
from pixelpersona.scraping.wikiquote import WikiquoteScraper
from pixelpersona.config import RAW_DATA_DIR


def save_raw_content(persona_name: str, source_name: str, result: dict):
    """Save raw scraped content to data/raw/{persona}/{source}.json"""
    raw_dir = RAW_DATA_DIR / persona_name.replace(" ", "_")
    raw_dir.mkdir(parents=True, exist_ok=True)

    output_file = raw_dir / f"{source_name}.json"

    # Prepare sections for JSON serialization
    sections = result.get("sections", {})
    sections_data = {
        "section_titles": list(sections.keys()) if isinstance(sections, dict) else [],
        "total_sections": len(sections) if isinstance(sections, dict) else 0,
        "sections_content": sections
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "persona": persona_name,
            "source": source_name,
            "url": result.get("url", ""),
            "title": result.get("title", ""),
            "content": result.get("content", ""),
            "sections": sections_data
        }, f, indent=2, ensure_ascii=False)

    return output_file


def scrape_persona(persona_name: str):
    """Scrape Wikipedia and Wikiquote for a persona."""
    print(f"Scraping sources for: {persona_name}")

    scrapers = {
        "wikipedia": WikipediaScraper(),
        "wikiquote": WikiquoteScraper()
    }

    raw_dir = RAW_DATA_DIR / persona_name.replace(" ", "_")
    raw_dir.mkdir(parents=True, exist_ok=True)

    files_saved = []

    for source_name, scraper in scrapers.items():
        print(f"  Scraping from {source_name}...")
        try:
            result = scraper.scrape(persona_name)
            if result and result.get("content"):
                raw_file = save_raw_content(persona_name, source_name, result)
                files_saved.append(str(raw_file))
                print(f"    Saved to {raw_file} ({len(result['content'])} chars)")
            else:
                print(f"    No content returned")
        except Exception as e:
            print(f"    Error: {e}")

    print(f"\nScraping complete for {persona_name}")
    print(f"Files saved to: {raw_dir}")
    return files_saved


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Wikipedia and Wikiquote for a persona")
    parser.add_argument("persona_name", help="Name of the persona to scrape")
    args = parser.parse_args()
    scrape_persona(args.persona_name)
