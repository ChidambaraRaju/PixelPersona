"""Scraping package."""
from pixelpersona.scraping.wikipedia import WikipediaScraper
from pixelpersona.scraping.wikiquote import WikiquoteScraper
from pixelpersona.scraping.primary_source import PrimarySourceScraper

__all__ = ["WikipediaScraper", "WikiquoteScraper", "PrimarySourceScraper"]