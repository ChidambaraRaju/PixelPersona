"""Scraping package."""
from pixelpersona.scraping.wikipedia import WikipediaScraper
from pixelpersona.scraping.wikiquote import WikiquoteScraper
from pixelpersona.scraping.gutenberg import GutenbergScraper

__all__ = ["WikipediaScraper", "WikiquoteScraper", "GutenbergScraper"]