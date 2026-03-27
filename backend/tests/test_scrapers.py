"""Tests for scrapers."""
import pytest
from pixelpersona.scraping.wikipedia import WikipediaScraper
from pixelpersona.scraping.wikiquote import WikiquoteScraper
from pixelpersona.scraping.primary_source import PrimarySourceScraper

@pytest.fixture
def wikipedia_scraper():
    return WikipediaScraper()

@pytest.fixture
def wikiquote_scraper():
    return WikiquoteScraper()

@pytest.fixture
def primary_source_scraper():
    return PrimarySourceScraper()

def test_wikipedia_scraper_returns_content(wikipedia_scraper):
    """Test that Wikipedia scraper returns expected structure."""
    result = wikipedia_scraper.scrape("Albert Einstein")
    assert "content" in result
    assert "url" in result
    # Content should be non-empty for a known person
    assert len(result["content"]) > 0

def test_wikipedia_scraper_unknown_person(wikipedia_scraper):
    """Test Wikipedia scraper with unknown person."""
    result = wikipedia_scraper.scrape("ThisPersonDoesNotExist12345XYZ")
    assert result["content"] == ""
    assert result["url"] == ""

def test_wikiquote_scraper_returns_content(wikiquote_scraper):
    """Test that Wikiquote scraper returns expected structure."""
    result = wikiquote_scraper.scrape("Albert Einstein")
    assert "content" in result
    assert "url" in result

def test_wikiquote_scraper_unknown_person(wikiquote_scraper):
    """Test Wikiquote scraper with unknown person."""
    result = wikiquote_scraper.scrape("ThisPersonDoesNotExist12345XYZ")
    assert result["content"] == ""
    assert result["url"] == ""

def test_primary_source_scraper_returns_structure(primary_source_scraper):
    """Test that PrimarySource scraper returns expected structure."""
    result = primary_source_scraper.scrape("Albert Einstein")
    assert "content" in result
    assert "url" in result