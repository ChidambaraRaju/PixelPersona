"""Wikipedia scraper using wikipedia-api."""
import wikipediaapi
from typing import Dict, Any, List

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

            # Use page.text for full article content (intro + all sections)
            full_content = page.text if page.text else ""

            # Extract sections recursively for metadata
            sections = self._extract_all_sections(page)

            return {
                "content": full_content,
                "url": page.fullurl,
                "sections": sections
            }
        except Exception as e:
            return {"content": "", "url": "", "sections": {}}

    def _extract_all_sections(self, page, max_depth: int = 3) -> Dict[str, Any]:
        """Recursively extract all sections and their content from Wikipedia page."""
        sections = {}

        def traverse_sections(section, depth=0, path=""):
            if depth > max_depth:
                return

            title = section.title if section.title else ""
            if not title:
                return

            # Build section path for nested sections
            section_path = f"{path}/{title}" if path else title

            # Get text content of this section (not including subsections)
            text_content = section.text if section.text else ""

            # Store section with its content and hierarchy info
            sections[section_path] = {
                "title": title,
                "level": section.level,
                "text": text_content,
                "text_length": len(text_content)
            }

            # Recursively process subsections
            for subsection in section.sections:
                traverse_sections(subsection, depth + 1, section_path)

        # Process all top-level sections
        for section in page.sections:
            traverse_sections(section)

        return sections

    def _extract_section_content(self, page) -> List[Dict[str, str]]:
        """Extract content organized by sections for chunking."""
        content_by_section = []

        def collect_content(section, depth=0, parent_title=""):
            title = section.title if section.title else ""
            text = section.text if section.text else ""

            if title and text:
                content_by_section.append({
                    "section": title,
                    "parent": parent_title,
                    "level": section.level,
                    "text": text
                })

            for subsection in section.sections:
                collect_content(subsection, depth + 1, title)

        for section in page.sections:
            collect_content(section)

        return content_by_section