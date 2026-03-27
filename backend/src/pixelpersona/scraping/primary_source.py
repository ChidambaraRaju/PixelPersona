"""Primary source scraper for Gutenberg and Archive.org."""
import re
import httpx
from typing import Dict, Any, Optional

USER_AGENT = "PixelPersona/1.0 (RAG chatbot project; mailto:example@example.com)"
MAX_CONTENT_LENGTH = 500_000  # Limit to 500K chars to avoid memory issues
FETCH_TIMEOUT = 30  # Max seconds to wait for content fetch (non-blocking)

class PrimarySourceScraper:
    """Scrapes primary source writings from Gutenberg or Archive.org.

    Fetches actual text content (books, autobiographies, writings) by the persona.
    Non-blocking: returns empty content gracefully if fetch times out.
    """

    def scrape(self, persona_name: str, timeout: int = FETCH_TIMEOUT) -> Dict[str, Any]:
        """Attempt to find and scrape Gutenberg content for a persona.

        Args:
            persona_name: Name of the persona to search for
            timeout: Max seconds to wait for content fetch (default 30).
                    If exceeded, returns empty content gracefully.
        """
        # Try Gutenberg search first
        gutenberg_result = self._search_gutenberg(persona_name, timeout=timeout)
        if gutenberg_result and gutenberg_result.get("content"):
            return gutenberg_result

        # Fallback to Archive.org (also respects timeout)
        return self._search_archive(persona_name, timeout=timeout)

    def _search_gutenberg(self, persona_name: str, timeout: int = FETCH_TIMEOUT) -> Optional[Dict[str, Any]]:
        """Search Gutenberg for persona works and fetch full text."""
        url = "https://gutendex.com/books"
        params = {"search": persona_name}
        headers = {"User-Agent": USER_AGENT}

        try:
            response = httpx.get(url, params=params, headers=headers, timeout=float(timeout), follow_redirects=True)
            if response.status_code != 200:
                return None

            data = response.json()
            results = data.get("results", [])
            if not results:
                return None

            # Try to find a book where the persona is an author
            # First pass: exact author match
            books_to_try = []
            for book in results:
                authors = book.get("authors", [])
                author_names = [a.get("name", "").lower() for a in authors]
                persona_lower = persona_name.lower()

                # Check if any author name contains the persona name
                is_author = any(persona_lower in name.lower() for name in author_names)
                books_to_try.append((book, is_author))

            # Sort: prefer books where persona is an author
            books_to_try.sort(key=lambda x: not x[1])

            # Try each book until we get valid content
            for book, _ in books_to_try:
                book_content = self._fetch_gutenberg_text(book, timeout=timeout)
                if book_content:
                    return book_content

        except Exception:
            pass

        return None

    def _fetch_gutenberg_text(self, book: Dict[str, Any], timeout: int = FETCH_TIMEOUT) -> Optional[Dict[str, Any]]:
        """Fetch full text from a Gutenberg book."""
        title = book.get("title", "")
        authors = book.get("authors", [])
        author_name = authors[0].get("name", "") if authors else ""
        formats = book.get("formats", {})

        # Find plain text URL (prefer UTF-8)
        txt_url = (
            formats.get("text/plain; charset=utf-8") or
            formats.get("text/plain; charset=us-ascii") or
            formats.get("text/plain")
        )

        if not txt_url:
            return None

        headers = {"User-Agent": USER_AGENT}

        try:
            response = httpx.get(txt_url, headers=headers, timeout=float(timeout), follow_redirects=True)
            if response.status_code != 200:
                return None

            content = response.text

            # Remove UTF-8 BOM if present
            if content and ord(content[0]) == 0xFEFF:
                content = content[1:]

            # Clean up Gutenberg text: remove header/footer metadata
            content = self._clean_gutenberg_text(content)

            if len(content) < 100:  # Too short, likely empty
                return None

            # Truncate if too long
            if len(content) > MAX_CONTENT_LENGTH:
                content = content[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated due to length...]"

            return {
                "content": content,
                "url": txt_url,
                "title": title,
                "author": author_name,
                "source": "gutenberg"
            }
        except Exception:
            return None

    def _clean_gutenberg_text(self, text: str) -> str:
        """Clean up Gutenberg plain text, removing headers and footers."""
        # Remove Project Gutenberg header
        header_patterns = [
            r".*?This eBook is for the use.*?anywhere\..*?\n\n",
            r".*?Project Gutenberg.*?\n\n",
            r".*?Most recently updated.*?\n\n",
        ]
        for pattern in header_patterns:
            text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)

        # Remove Project Gutenberg footer (typically at end)
        footer_patterns = [
            r"\n\n\*\*\* End of.*?Project Gutenberg.*?\*\*\*.*$",
            r"\n\n\*\*\* END OF.*?\*\*\*.*$",
            r"\n\nEnd of the Project Gutenberg.*?$",
        ]
        for pattern in footer_patterns:
            text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)

        # Remove excessive whitespace
        text = re.sub(r"\n{4,}", "\n\n\n", text)
        text = text.strip()

        return text

    def _search_archive(self, persona_name: str, timeout: int = FETCH_TIMEOUT) -> Dict[str, Any]:
        """Search Archive.org for persona content and fetch full text."""
        url = "https://archive.org/advancedsearch.php"
        params = {
            "q": f'"{persona_name}" OR {persona_name}',
            "fl[]": "identifier,title,downloads",
            "output": "json",
            "rows": 5,
            "sort": "downloads desc"
        }
        headers = {"User-Agent": USER_AGENT}

        try:
            response = httpx.get(url, params=params, headers=headers, timeout=float(timeout))
            if response.status_code != 200:
                return {"content": "", "url": ""}

            data = response.json()
            docs = data.get("response", {}).get("docs", [])
            if not docs:
                return {"content": "", "url": ""}

            # Try each doc until we get valid content
            for doc in docs:
                identifier = doc.get("identifier")
                title = doc.get("title", "")
                if identifier:
                    text_content = self._fetch_archive_text(identifier, title, timeout=timeout)
                    if text_content:
                        return text_content

        except Exception:
            pass

        return {"content": "", "url": ""}

    def _fetch_archive_text(self, identifier: str, title: str = "", timeout: int = FETCH_TIMEOUT) -> Optional[Dict[str, Any]]:
        """Fetch full text from an Archive.org item."""
        # First try to get the OCR text directly
        headers = {"User-Agent": USER_AGENT}

        # Try the download endpoint for text
        text_urls = [
            f"https://archive.org/download/{identifier}/{identifier}_djvu.txt",
            f"https://archive.org/download/{identifier}/{identifier}_text",
        ]

        for txt_url in text_urls:
            try:
                response = httpx.get(txt_url, headers=headers, timeout=float(timeout), follow_redirects=True)
                if response.status_code == 200:
                    content = response.text

                    if len(content) < 100:
                        continue

                    # Truncate if too long
                    if len(content) > MAX_CONTENT_LENGTH:
                        content = content[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated due to length...]"

                    return {
                        "content": content,
                        "url": f"https://archive.org/details/{identifier}",
                        "title": title,
                        "source": "archive.org"
                    }
            except Exception:
                continue

        # If direct text failed, try the metadata API to find text files
        try:
            metadata_url = f"https://archive.org/metadata/{identifier}"
            response = httpx.get(metadata_url, headers=headers, timeout=float(timeout))
            if response.status_code == 200:
                metadata = response.json()
                files = metadata.get("files", [])

                # Look for text/ocr files
                for f in files:
                    fname = f.get("name", "")
                    fmt = f.get("format", "")
                    if "text" in fmt.lower() or fname.endswith(".txt"):
                        # Try to fetch this file
                        file_url = f"https://archive.org/download/{identifier}/{fname}"
                        file_response = httpx.get(file_url, headers=headers, timeout=float(timeout), follow_redirects=True)
                        if file_response.status_code == 200:
                            content = file_response.text
                            if len(content) > 100:
                                if len(content) > MAX_CONTENT_LENGTH:
                                    content = content[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated due to length...]"
                                return {
                                    "content": content,
                                    "url": f"https://archive.org/details/{identifier}",
                                    "title": title,
                                    "source": "archive.org"
                                }
        except Exception:
            pass

        return None
