from datetime import datetime
import logging
import requests
from typing import List
import xmltodict as x2d

from processors.base_processor import Processor
from schema import Paper
from utils import scrape_arXiv_ids


logger = logging.getLogger(__name__)


class ArXivProcessor(Processor):
    """
    Processor for scraping and processing papers from ArXiv using Firecrawl.
    """

    def fetch(self) -> str:
        """
        Fetch cleaned markdown data from the ArXiv source using Firecrawl. Results are a
        map from url to page content
        """
        paper_ids = []
        last_url = None
        try:
            for url in self.urls:
                last_url = f"{url}?max_results=200"
                logging.info(f"Fetching data from {last_url}")
                paper_ids.extend(scrape_arXiv_ids(last_url))
            paper_ids = list(set(paper_ids))
            raw_data = self.get_several_papers_by_id(paper_ids)
            return raw_data

        except Exception as e:
            logging.error(f"Failed to fetch data from {last_url}: {e}")
            return ""

    def get_several_papers_by_id(self, paper_ids: List[str]) -> str:
        url = f"https://export.arxiv.org/api/query?max_results={len(paper_ids)}&id_list={','.join(paper_ids)}"
        data = requests.get(url)
        return data.text

    def parse(self, raw_data: str) -> List[Paper]:
        """
        Parse the cleaned markdown data from Firecrawl into paper metadata.

        Args:
            raw_data (str): Cleaned markdown string from Firecrawl.

        Returns:
            Paper: List of paper metadata dictionaries.
        """
        # Ensure the input is valid
        if not raw_data:
            return []

        papers = []
        entries = x2d.parse(raw_data)["feed"]["entry"]
        if type(entries) != list:
            entries = [entries]  # kind of lame
        for entry in entries:
            #logger.info(f"Parsing paper: {}")
            try:
                abstract_link = entry["id"]
                title = entry["title"]
                abstract = entry["summary"]
                publish_date = datetime.strptime(entry["published"], "%Y-%m-%dT%H:%M:%SZ")
                pdf_link = next(filter(lambda x: x.get("@type") == "application/pdf", entry["link"]))["@href"]

                # Authors is either a dict or a list
                authors = []
                if type(entry["author"]) == list:
                    authors = [a["name"] for a in entry["author"]]
                elif type(entry["author"]) == dict:
                    authors = [entry["author"]["name"]]
                else:
                    raise TypeError("Authors is neither a list nor a dict.")

                papers.append(Paper(
                    title=title,
                    authors=authors,
                    full_text_link=pdf_link,
                    abstract_link= abstract_link,
                    published=publish_date,
                    abstract=abstract
                ))
            except Exception as e:
                logger.error(f"Failed to parse paper{entry['id']} because: {e}")

        return papers


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    # Mock configuration and state
    state = {"last_run": "2025-07-25"}
    urls = ["https://arxiv.org/list/cs.MA/recent"]

    # Initialize processor
    arxiv_processor = ArXivProcessor(state=state, urls=urls)

    logging.info("Fetching papers...")
    raw_data = arxiv_processor.fetch()

    if raw_data:
        logging.info("Parsing papers...")
        papers = arxiv_processor.parse(raw_data)

        logging.info(f"Found {len(papers)} papers.")
        new_papers = [paper for paper in papers if arxiv_processor.paper_is_new(paper)][:2]

        logging.info(f"Filtered down to {len(new_papers)} new and relevant papers.")
    else:
        logging.error("Failed to fetch data from ArXiv.")