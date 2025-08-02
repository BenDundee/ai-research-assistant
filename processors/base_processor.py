from abc import ABC, abstractmethod
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any


class Processor(ABC):
    """
    Abstract base class for all processors.
    """

    def __init__(self, config: Dict[str, Any], state: Dict[str, Any]):
        """
        Initialize the processor with configuration and state.

        Args:
            config (dict): Configuration for the processor, e.g., source URL.
            state (dict): Run-time state, e.g., last_run date.
        """
        self.config = config
        self.state = state
        self.last_run = self._get_last_run_date()

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

    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch raw data from the given source.
        Returns a list of papers as dictionaries.
        """
        pass

    @abstractmethod
    def parse(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        Parse raw fetched data into normalized paper dicts.

        Returns:
            List[Dict[str, Any]]: A list of {title, abstract, link, date}.
        """
        pass

    def paper_is_new(self, paper_date: datetime) -> bool:
        """
        Check if a paper's date is newer than the last run date.

        Args:
            paper_date (datetime): The publication date of the paper.

        Returns:
            bool: True if the paper is new, False otherwise.
        """
        return paper_date > self.last_run

    @abstractmethod
    def topic_match(self, topics: List[str], paper: Dict[str, Any]) -> bool:
        """
        Check if the paper matches any of the given topics.

        Args:
            topics (List[str]): High-recall topic keywords.
            paper (Dict[str, Any]): Normalized paper dictionary.

        Returns:
            bool: True if the paper matches, False otherwise.
        """
        pass

    @abstractmethod
    def summarize_and_score(self, topics: List[str], paper: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use an LLM to summarize and score the paper for relevance.

        Args:
            topics (List[str]): Topics of interest.
            paper (Dict[str, Any]): Normalized paper dictionary.

        Returns:
            Dict[str, Any]: Paper dict with added relevance and summary fields.
        """
        pass