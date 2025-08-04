import logging
from typing import List

from agents import deep_diver
from processors import load_processors
from utils import load_config, update_last_run


logger = logging.getLogger(__name__)

RELEVANCE_CUTOFF = 75  # TODO: move to some config or something

class Controller:

    def __init__(self):
        self.state = load_config("state.yaml")
        self.processor_config = load_config("processor.yaml")
        self.processors = load_processors(self.state, self.processor_config)

    def search(self) -> List[str]:
        relevant_papers = []
        for name, proc in self.processors.items():
            logger.info(f"Fetching data from {name}...")
            raw_data = proc.fetch()
            if raw_data:
                papers = proc.parse(raw_data)
                logger.info(f"Found {len(papers)} papers from {name}, summarizing and scoring...")
                papers = proc.summarize_and_score_all(papers)
                relevant_papers = list(filter(lambda x: x.relevance >= RELEVANCE_CUTOFF, papers))
                relevant_papers.sort(key=lambda x: x.relevance, reverse=True)
                logger.info(f"Isolated {len(relevant_papers)} relevant papers from {name}.")
            else:
                logger.warning(f"************************ Failed to fetch data from {name}.")
        self.state = update_last_run()
        return [p.pretty_print() for p in relevant_papers]

    def deep_dive(self, paper_url: str) -> str:
        """ Perform a deep dive on a specific paper

        Do the following:
            - Read the paper (send into LLM and get a summary plus a collection of relevant search terms)
            - Update the database of arxiv papers (download from kagglehub)
            - Build a vector DB
            - Execute searches against the vector DB
            - Get relevant papers
            - LLM to summarize each paper and assign a relevance score
            - Download relevant papers and save to disk

        :param paper_url:
        :return:
        """
        return deep_diver(paper_url)


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    controller = Controller()
    results = controller.search()

    with open("results.txt", "w") as f:
        f.write("\n".join(results))
