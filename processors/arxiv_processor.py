from datetime import datetime
from typing import List, Dict, Any
import logging
from processors.base_processor import Processor
from utils.fetcher import fetch_page
from summarizer.summarizer import get_summary_and_relevance
from schema import Paper
import requests
import xmltodict as x2d


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
        url = self.config["url"]
        logging.info(f"Fetching data from {url}")
        
        try:
            raw_data = fetch_page(url).strip()
            paper_ids = []
            lines = raw_data.splitlines()
            for line in lines:
                # Pull off paper_ids, then read abstracts.
                # Should look like this
                # '\\[1\\] [arXiv:2507.23785](https://arxiv.org/abs/2507.23785 "Abstract")'
                if "https://arxiv.org/abs/" in line:
                    paper_id = line.split("arXiv:")[1].split("]")[0]
                    paper_ids.append(paper_id)

            # Now get paper metadata, no need to scrape here...
            url = f"https://export.arxiv.org/api/query?id_list={','.join(paper_ids)}"
            data = requests.get(url)
            return data.text
        except Exception as e:
            logging.error(f"Failed to fetch data from {url}: {e}")
            return ""

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
        for entry in entries:
            #logger.info(f"Parsing paper: {}")
            abstract_link = entry["id"]
            title = entry["title"]
            authors = [a["name"] for a in entry["author"]]
            abstract = entry["summary"]
            publish_date = datetime.strptime(entry["published"], "%Y-%m-%dT%H:%M:%SZ")
            pdf_link = next(filter(lambda x: x["@type"] == "application/pdf", entry["link"]))["@href"]

            papers.append(Paper(
                title=title,
                authors=authors,
                full_text_link=pdf_link,
                abstract_link= abstract_link,
                published=publish_date,
                abstract=abstract
            ))

        return papers

    async def _async_summarize_and_score(self, paper: Paper) -> Paper:
        """
        Use OpenRouter (LLM) to assign a relevance score and generate a summary.

        Args:
            paper (Paper): Metadata of a paper.

        Returns:
            Paper: Metadata with added summary and relevance.
        """
        return get_summary_and_relevance(paper)

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    # Mock configuration and state
    config = {"url": "https://arxiv.org/list/cs/recent"}
    state = {"last_run": "2025-07-25"}

    # Initialize processor
    arxiv_processor = ArXivProcessor(config=config, state=state)

    logging.info("Fetching papers...")
    raw_data = arxiv_processor.fetch()

    if raw_data:
        logging.info("Parsing papers...")
        papers = arxiv_processor.parse(raw_data)

        logging.info(f"Found {len(papers)} papers.")
        new_papers = [paper for paper in papers if arxiv_processor.paper_is_new(paper)][:2]

        logging.info(f"Filtered down to {len(new_papers)} new and relevant papers.")

        # Call synchronous summarize_and_score_all
        results = arxiv_processor.summarize_and_score_all(new_papers)
        for paper in results:
            logging.info(f"Title: {paper.title}")
            logging.info(f"Summary: {paper.summary}")
            logging.info(f"Relevance: {paper.relevance}")
    else:
        logging.error("Failed to fetch data from ArXiv.")