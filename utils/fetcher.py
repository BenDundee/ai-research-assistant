import requests
import logging
import yaml

def fetch_firecrawl_api_key() -> str:
    """
    Load the Firecrawl API key from `config/secrets.yaml`.

    Returns:
        str: The API key.
    """
    try:
        with open("config/secrets.yaml", "r") as file:
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

    api_url = "https://api.firecrawl.com/scrape"
    payload = {"url": url, "formats": ["markdown"]}
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch data from Firecrawl API for {url}: {e}")
        return ""
    

if __name__ == "__main__":
    # A basic test for the fetch_page functionality
    logging.basicConfig(level=logging.INFO)

    # Replace with a URL that works with Firecrawl
    test_url = "https://simonwillison.net/2024/Jan/6/scraping-explained/"

    try:
        result = fetch_page(test_url)
        if result:
            print("Fetched Markdown:")
            print(result[:500])  # Print the first 500 characters
        else:
            print("Fetching failed or returned an empty result.")
    except Exception as e:
        print(f"Error occurred during fetch_page test: {e}")