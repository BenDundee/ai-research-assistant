import requests
import logging
import yaml
from pathlib import Path

from firecrawl import FirecrawlApp, ScrapeOptions


base_dir = Path(__file__).parent.parent.resolve()
config_dir = base_dir / "config"

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
    

if __name__ == "__main__":
    # A basic test for the fetch_page functionality
    logging.basicConfig(level=logging.INFO)

    # Replace with a URL that works with Firecrawl
    test_url = "https://en.wikipedia.org/wiki/Web_scraping"

    try:
        result = fetch_page(test_url)
        if result:
            print("Fetched Markdown:")
            print(result[:500])  # Print the first 500 characters
        else:
            print("Fetching failed or returned an empty result.")
    except Exception as e:
        print(f"Error occurred during fetch_page test: {e}")