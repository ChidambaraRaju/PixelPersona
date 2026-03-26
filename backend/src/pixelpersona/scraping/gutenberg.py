"""Gutenberg/Archive.org scraper."""
import httpx
from typing import Dict, Any, Optional

class GutenbergScraper:
    """Scrapes autobiographies and primary sources from Gutenberg or Archive.org."""

    def scrape(self, persona_name: str) -> Dict[str, Any]:
        """Attempt to find and scrape Gutenberg content for a persona."""
        # Try Gutenberg search first
        gutenberg_result = self._search_gutenberg(persona_name)
        if gutenberg_result:
            return gutenberg_result

        # Fallback to Archive.org
        return self._search_archive(persona_name)

    def _search_gutenberg(self, persona_name: str) -> Optional[Dict[str, Any]]:
        """Search Gutenberg for persona works."""
        url = "https://gutendex.com/books"
        params = {"search": persona_name}

        try:
            response = httpx.get(url, params=params, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if results:
                    # Return first relevant result
                    book = results[0]
                    title = book.get('title', '')
                    authors = book.get('authors', [])
                    author_name = authors[0].get('name', '') if authors else ''
                    return {
                        "content": f"{title}. By {author_name}",
                        "url": book.get("url", ""),
                        "title": title
                    }
        except Exception:
            pass

        return None

    def _search_archive(self, persona_name: str) -> Dict[str, Any]:
        """Search Archive.org for persona content."""
        url = "https://archive.org/advancedsearch.php"
        params = {
            "q": f"{persona_name} autobiography",
            "fl[]": "title,identifier,downloads",
            "output": "json",
            "rows": 1
        }

        try:
            response = httpx.get(url, params=params, timeout=30.0)
            if response.status_code == 200:
                data = response.json()
                docs = data.get("response", {}).get("docs", [])
                if docs:
                    doc = docs[0]
                    return {
                        "content": f"Archive.org: {doc.get('title', '')}",
                        "url": f"https://archive.org/details/{doc.get('identifier', '')}",
                        "title": doc.get("title", "")
                    }
        except Exception:
            pass

        return {"content": "", "url": ""}