"""Wikiquote scraper."""
import httpx
from typing import Dict, Any

class WikiquoteScraper:
    """Scrapes quotes from Wikiquote."""

    def scrape(self, persona_name: str) -> Dict[str, Any]:
        """Scrape Wikiquote page for a persona."""
        url = "https://en.wikiquote.org/w/api.php"
        params = {
            "action": "query",
            "titles": persona_name,
            "prop": "extracts",
            "exintro": False,
            "format": "json"
        }

        try:
            response = httpx.get(url, params=params, timeout=30.0)
            data = response.json()

            pages = data.get("query", {}).get("pages", {})
            for page_data in pages.values():
                if "extract" in page_data:
                    return {
                        "content": page_data["extract"],
                        "url": f"https://en.wikiquote.org/wiki/{persona_name}"
                    }
        except Exception:
            pass

        return {"content": "", "url": ""}