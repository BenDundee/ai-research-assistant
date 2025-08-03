from typing import Dict, List

# Processors
from .arxiv_processor import ArXivProcessor

from .base_processor import Processor


def load_processors(state: Dict[str, str], config: Dict[str, List[str]]) -> Dict[str, Processor]:
    arxiv_urls = config.get("arxiv", [])
    return {
        "arXiv": ArXivProcessor(state, arxiv_urls)
    }