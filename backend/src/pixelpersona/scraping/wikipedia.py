"""Wikipedia scraper using wikipedia-api."""
import wikipediaapi
from typing import Dict, Any

class WikipediaScraper:
    """Scrapes biography and works from Wikipedia."""

    def __init__(self, user_agent: str = "PixelPersona/1.0 (RAG chatbot project)"):
        self.wiki = wikipediaapi.Wikipedia(user_agent=user_agent, language='en')

    def scrape(self, persona_name: str) -> Dict[str, Any]:
        """Scrape Wikipedia article for a persona."""
        try:
            page = self.wiki.page(persona_name)
            if not page.exists():
                return {"content": "", "url": "", "sections": {}}

            return {
                "content": page.summary if page.summary else "",
                "url": page.fullurl,
                "sections": self._extract_sections(page)
            }
        except Exception:
            return {"content": "", "url": "", "sections": {}}

    def _extract_sections(self, page) -> Dict[str, str]:
        """Extract relevant sections from Wikipedia page."""
        sections = {}
        try:
            for section in page.sections:
                title_lower = section.title.lower() if section.title else ""
                if title_lower in ["biography", "works", "career", "life", "early life", "achievements"]:
                    sections[section.title] = section.text
        except Exception:
            pass
        return sections