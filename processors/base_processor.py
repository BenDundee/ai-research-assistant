from abc import ABC, abstractmethod
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from schema import Paper
import concurrent.futures
from utils import update_last_run


class Processor(ABC):
    """
    Abstract base class for all processors.
    """

    def __init__(self, state: Dict[str, Any], urls: List[str]):
        """
        Initialize the processor with configuration and state.

        Args:
            state (dict): Run-time state, e.g., last_run date.
            urls (List[str]): urls to scrape
        """
        self.state = state
        self.urls = urls
        self.last_run = self._get_last_run_date()

    @abstractmethod
    def fetch(self) -> str:
        """
        Fetch raw data from the given source.
        """
        pass

    @abstractmethod
    def parse(self, raw_data: str) -> List[Paper]:
        """
        Parse raw fetched data into normalized paper dicts.

        Returns:
            List[Paper]: A list of Paper objects
        """
        pass

    @abstractmethod
    async def _async_summarize_and_score(self, paper: Paper) -> Paper:
        """
        Asynchronous method to use an LLM to summarize and score the paper.

        Args:
            paper (Paper): Metadata of a paper.

        Returns:
            Paper: Paper object with added summary and relevance.
        """
        pass

    def paper_is_new(self, paper: Paper) -> bool:
        """
        Check if a paper's date is newer than the last run date.

        Args:
            paper_date (datetime): The publication date of the paper.

        Returns:
            bool: True if the paper is new, False otherwise.
        """
        return paper.published >= self.last_run

    def _get_last_run_date(self) -> datetime:
        """
        Get the last run date from the state, or default to one week ago.
        """
        try:
            last_run_str = self.state.get("last_run")
            if last_run_str:
                return datetime.strptime(last_run_str, "%Y-%m-%d")
        except Exception as e:
            logging.warning(f"Failed to parse last_run date: {e}")

        # Default to one week ago
        logging.warning("last_run date not found: defaulting to one week ago.")
        return datetime.now() - timedelta(days=7)

    async def _async_summarize_and_score_all(self, papers: List[Paper]) -> List[Paper]:
        """
        Asynchronous method to summarize and score all papers.

        Args:
            papers (List[Paper]): List of papers to process.

        Returns:
            List[Paper]: Processed papers with summaries and scores.
        """
        return await asyncio.gather(
            *(self._async_summarize_and_score(paper) for paper in papers)
        )

    def summarize_and_score_all(self, papers: List[Paper]) -> List[Paper]:
        """
        Synchronous wrapper that uses threading to process papers in parallel.

        Args:
            papers (List[Paper]): List of papers to process.

        Returns:
            List[Paper]: Processed papers with summaries and scores.
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            # Map each paper to `_sync_summarize_and_score` in parallel
            results = list(executor.map(self.summarize_and_score, papers))
        return results

    def summarize_and_score(self, paper: Paper) -> Paper:
        """
        Synchronous wrapper for the asynchronous `_async_summarize_and_score`.

        Args:
            paper (Paper): Metadata of a paper.

        Returns:
            Paper: Paper object with added summary and relevance.
        """
        return asyncio.run(self._async_summarize_and_score(paper))
