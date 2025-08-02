import requests
import logging
import yaml
from pathlib import Path
from typing import List, Dict
import logging

from firecrawl import FirecrawlApp


base_dir = Path(__file__).parent.parent.resolve()
config_dir = base_dir / "config"

logger = logging.getLogger(__name__)


def fetch_firecrawl_api_key() -> str:
    """
    Load the Firecrawl API key from `config/secrets.yaml`.

    Returns:
        str: The API key.
    """
    try:
        with open(config_dir / "secrets.yaml", "r") as file:
            secrets = yaml.safe_load(file)
            return secrets.get("firecrawl_api_key", "")
    except Exception as e:
        logging.error(f"Failed to load Firecrawl API key from secrets.yaml: {e}")
        return ""


def fetch_page(url: str) -> str:
    """
    Fetch cleaned markdown from a given URL using the Firecrawl API.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: Cleaned markdown response.
    """
    api_key = fetch_firecrawl_api_key()
    if not api_key:
        raise ValueError("Firecrawl API key not found in `secrets.yaml`.")

    try:
        app = FirecrawlApp(api_key=api_key)
        result = app.scrape_url(url, formats=['markdown', 'html'])
        return result.markdown
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data from Firecrawl API for {url}: {e}")
        return ""


def fetch_pages(urls: List[str]) -> Dict[str, str]:
    api_key = fetch_firecrawl_api_key()
    if not api_key:
        raise ValueError("Firecrawl API key not found in `secrets.yaml`.")

    try:
        app = FirecrawlApp(api_key=api_key)
        results = app.batch_scrape_urls(urls, formats=['markdown', 'html'])
        if not results.success:
            raise RuntimeError(f"Failed to fetch data from Firecrawl API: {results.error}")
        output = {}
        for pg in results.data:
            output[pg.metadata["url"]] = pg.markdown
        return output
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data from Firecrawl API for {url}: {e}")
        return {}
    

if __name__ == "__main__":
    # A basic test for the fetch_page functionality
    logging.basicConfig(level=logging.INFO)

    test_url = "https://en.wikipedia.org/wiki/Web_scraping"
    test_urls = [
        "https://en.wikipedia.org/wiki/Web_scraping",
        "https://en.wikipedia.org/wiki/Artificial_intelligence"
    ]

    if False:
        try:
            result = fetch_page(test_url)
            if result:
                print("Fetched Markdown:")
                print(result[:500])  # Print the first 500 characters
            else:
                print("Fetching failed or returned an empty result.")
        except Exception as e:
            print(f"Error occurred during fetch_page test: {e}")

    if True:
        results = fetch_pages(test_urls)
        for url, result in results.items():
            print(f"Fetched Markdown for {url}:")
            print(result[:500])