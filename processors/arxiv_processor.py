from datetime import datetime
from typing import List, Dict, Any
import logging
from processors.base_processor import Processor
from utils.fetcher import fetch_page  # Firecrawl integration for fetching clean markdown


class ArxivProcessor(Processor):
    """
    Processor for scraping and processing papers from ArXiv using Firecrawl.
    """

    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch cleaned markdown data from the ArXiv source using Firecrawl.
        """
        url = self.config["url"]
        logging.info(f"Fetching data from {url}")
        
        try:
            raw_data = fetch_page(url)
            return raw_data.strip()  # Return cleaned output
        except Exception as e:
            logging.error(f"Failed to fetch data from {url}: {e}")
            return ""

    def parse(self, raw_data: str) -> List[Dict[str, Any]]:
        """
        Parse the cleaned markdown data from Firecrawl into paper metadata.
        
        Args:
            raw_data (str): Cleaned markdown string from Firecrawl.

        Returns:
            List[Dict[str, Any]]: Normalized paper dictionaries.
        """
        # Ensure the input is valid
        if not raw_data:
            return []

        papers = []
        lines = raw_data.splitlines()
        current_paper = {}

        for line in lines:
            line = line.strip()

            # Parse metadata (e.g., titles, abstracts, and links)
            if line.startswith("Title:"):
                if current_paper:  # Save the previous paper if complete
                    papers.append(current_paper)
                    current_paper = {}

                current_paper["title"] = line.replace("Title:", "").strip()

            elif line.startswith("Abstract:"):
                current_paper["abstract"] = line.replace("Abstract:", "").strip()

            elif line.startswith("Link:"):
                current_paper["link"] = line.replace("Link:", "").strip()

            elif "Submitted on" in line:  # Parse the submission date
                try:
                    date_str = line.split("Submitted on")[-1].strip()
                    current_paper["date"] = datetime.strptime(
                        date_str, "%d %b %Y"
                    ).date()
                except Exception as e:
                    logging.warning(f"Failed to parse date from line '{line}': {e}")

        # Add the last paper
        if current_paper:
            papers.append(current_paper)

        return papers

    def topic_match(self, topics: List[str], paper: Dict[str, Any]) -> bool:
        """
        Check if the paper matches any of the given topics based on title or abstract.

        Args:
            topics (List[str]): List of topic keywords.
            paper (Dict[str, Any]): Metadata of a single paper.

        Returns:
            bool: True if a match is found.
        """
        for topic in topics:
            if topic.lower() in paper["title"].lower() or topic.lower() in paper["abstract"].lower():
                return True
        return False

    def summarize_and_score(self, topics: List[str], paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use OpenRouter (LLM) to assign a relevance score and generate a summary.

        Args:
            topics (List[str]): Topics of interest.
            paper (Dict[str, Any]): Metadata of a paper.

        Returns:
            Dict[str, Any]: Paper dict with added "relevance" and "summary".
        """
        from summarizer.summarizer import get_summary_and_relevance

        prompt_input = {
            "topics": ", ".join(topics),
            "title": paper["title"],
            "abstract": paper["abstract"],
            "link": paper["link"],
        }

        summary_result = get_summary_and_relevance(prompt_input)
        paper.update(summary_result)

        return paper

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)

    # Mock configuration and state
    config = {
        "url": "https://arxiv.org/list/cs/recent",
    }
    state = {
        "last_run": "2025-07-25"  # One week prior to today for testing
    }

    # Topics for filtering
    topics = ["chatbot", "reasoning", "large language models"]

    # Initialize and test ArxivProcessor
    arxiv_processor = ArxivProcessor(config=config, state=state)

    logging.info("Fetching papers...")
    raw_data = arxiv_processor.fetch()

    if raw_data:
        logging.info("Parsing papers...")
        papers = arxiv_processor.parse(raw_data)

        logging.info(f"Found {len(papers)} papers.")
        new_papers = [
            paper
            for paper in papers
            if arxiv_processor.paper_is_new(paper["date"]) and arxiv_processor.topic_match(topics, paper)
        ]

        logging.info(f"Filtered down to {len(new_papers)} new and relevant papers.")

        for paper in new_papers[:3]:  # Display first 3 papers for demonstration
            logging.info(f"Title: {paper['title']}")
            logging.info(f"Abstract: {paper['abstract'][:200]}...")  # Show first 200 chars of abstract
            logging.info(f"Link: {paper['link']}")
    else:
        logging.error("Failed to fetch data from ArXiv.")