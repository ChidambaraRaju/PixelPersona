"""Wikiquote scraper."""
import re
import httpx
from typing import Dict, Any

USER_AGENT = "PixelPersona/1.0 (RAG chatbot project; mailto:example@example.com)"

class WikiquoteScraper:
    """Scrapes quotes from Wikiquote (Quotes section only, not intro)."""

    def scrape(self, persona_name: str) -> Dict[str, Any]:
        """Scrape Quotes section from Wikiquote page for a persona.

        Uses action=parse with section=1 to get the Quotes section directly,
        bypassing the intro which duplicates Wikipedia content.
        """
        url = "https://en.wikiquote.org/w/api.php"
        params = {
            "action": "parse",
            "page": persona_name,
            "prop": "text",
            "section": 1,  # Quotes section is always section 1 on Wikiquote
            "format": "json"
        }

        headers = {
            "User-Agent": USER_AGENT
        }

        try:
            response = httpx.get(url, params=params, headers=headers, timeout=30.0)
            data = response.json()

            html_content = data.get("parse", {}).get("text", {}).get("*", "")
            if not html_content:
                return {"content": "", "url": ""}

            # Strip HTML tags and clean up whitespace
            clean_content = self._strip_html(html_content)

            # Skip if content is just the page title without actual quotes
            if len(clean_content) < 50:
                return {"content": "", "url": ""}

            return {
                "content": clean_content,
                "url": f"https://en.wikiquote.org/wiki/{persona_name}",
                "title": f"{persona_name} - Quotes"
            }
        except Exception:
            pass

        return {"content": "", "url": ""}

    def _strip_html(self, html: str) -> str:
        """Remove HTML tags and clean up whitespace."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Decode common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = text.replace('&mdash;', '—')
        text = text.replace('&ndash;', '–')
        text = text.replace('&hellip;', '...')
        # Clean up multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text).strip()
        return text
