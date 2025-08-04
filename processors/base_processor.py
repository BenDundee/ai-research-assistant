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


