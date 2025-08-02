from typing import Dict

# Processors
from .arxiv_processor import ArXivProcessor

from .base_processor import Processor


def load_processors(state: Dict[str, str]) -> Dict[str, Processor]:
    return {
        "arXiv": ArXivProcessor(state)
    }