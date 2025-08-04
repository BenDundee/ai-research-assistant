import logging
from pathlib import Path
import requests
from typing import List

from bs4 import BeautifulSoup


base_dir = Path(__file__).parent.parent.resolve()
config_dir = base_dir / "config"

logger = logging.getLogger(__name__)


def scrape_arXiv_ids(page_url: str):
    try:
        # Send an HTTP GET request to the URL
        response = requests.get(page_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Extract Ids
            return extract_ids(response.content)
        else:
            print(f"Failed to retrieve HTML content. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def extract_ids(raw_html_from_arXiv: str) -> List[str]:
    # Parse HTML content with BeautifulSoup
    soup = BeautifulSoup(raw_html_from_arXiv, 'html.parser')

    # Find all dl tags containing dt tags
    dl_tags = soup.find_all('dl')

    # List to store extracted IDs
    extracted_ids = []

    # Iterate through dl tags
    for dl_tag in dl_tags:
        # Find all dt tags within the current dl tag
        dt_tags = dl_tag.find_all('dt')

        # Iterate through dt tags
        for dt_tag in dt_tags:

            a_tags = dt_tag.find_all('a', href=True)
            # first element: <a href="/abs/2508.00280" id="2508.00280" title="Abstract">arXiv:2508.00280</a>
            _id = a_tags[0].get("id")
            if _id:
                extracted_ids.append(_id)

    return extracted_ids
    

if __name__ == "__main__":
    # A basic test for the fetch_page functionality
    logging.basicConfig(level=logging.INFO)

    test_url = "https://arxiv.org/list/cs.MA/recent?max_results=200"

    try:
        result = scrape_arXiv_ids(test_url)
        if result:
            print("Fetched IDs:")
            print(result)  # Print the first 500 characters
        else:
            print("Fetching failed or returned an empty result.")
    except Exception as e:
        print(f"Error occurred during fetch_page test: {e}")
